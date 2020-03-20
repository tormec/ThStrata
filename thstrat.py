class Transmittance(object):
    """Calculate the transmittance of a stratigraphy with material
    in series or in parallel.

    The stratigraphy is described by a pattern with the following conventions:
    * comma separated values: materials in series
    * double-slash separetd values: material in parallel
    * comma separated values in brackets: material in series within parallel
    For instance:
    pattern = "1,(2,3,4)//5//(6,7),8"

    The indexes used in the pattern are different from the ones used to
    identify different materials.
    For instance:
    pattern = "1,2,3"
    stratigraphy = {
        "1": {"mat": 1, "thk": 1, "area": 1, "cnd": .01},
        "2": {"mat": 2, "thk": 1, "area": 1, "rst": .02},
        "3": {"mat": 1, "thk": 1, "area": 1, "cnd": .01}
        }
    where:
    "mat": material
    "thk": thickness
    "area"
    "cnd": conducttivity
    "rst": resistance
    """
    def __init__(self, pattern, strat, area):
        self.transmittance = 1 / self.resistance(pattern, strat, area)
        print(self.transmittance)
        print(strat)

    def resistance(self, pattern, strat, area):
        """Calculate the resistance of a given pattern of a stratigraphy.

        :param pattern (str): description of how materials are set out
        :param strat (dict): info relative to each index in the pattern
        :param area (float): surface of the stratigraphy
        :return resistante (flot): the resistance [(m^2 K)/W]
        """
        pattern = pattern.replace(" ", "")
        pattern = self.split_series(pattern)

        # calc the resistance of the structure
        rst = []
        for i in pattern:
            i = i.split("//")
            if len(i) > 1:  # indexes in parallel
                p_rst = []
                for p in i:
                    p = p.strip("()").split(",")
                    if len(p) > 1:  # indexes in series in parallel
                        s_rst = []
                        for s in p:
                            s_rst.append(self.rst_material(strat, s))
                        p_rst.append(1 / sum(s_rst))
                    else:
                        p_rst.append(1 / self.rst_material(strat, p[0]))
                rst.append(1 / sum(p_rst))
            else:
                rst.append(self.rst_material(strat, i[0]))
        tot_rst = sum(rst) * area  # (m^2 K)/W
        return tot_rst

    def split_series(self, pattern):
        """Split the pattern into indexes in series.

        For instance:
        "1,(2,3,4)//5//(6,7),8"
        is splitted in:
        ["1", "(2,3,4)//5//(6,7)", "8"]

        :param pattern (str): description of how materials are set out
        :return series (list): indexes or chunks of the pattern in series
        """
        series = []
        idx = ""
        inparallel = 0
        for i, v in enumerate(pattern):
            if v == "," and inparallel == 0:
                series.append(idx)
                idx = ""
            elif v == "(":
                inparallel = 1
                idx = idx + str(v)
            elif v == ")" and pattern[i+1] == ",":
                inparallel = 0
                idx = idx + str(v)
            elif i == len(pattern) - 1:
                idx = idx + str(v)
                series.append(idx)
            else:
                idx = idx + str(v)
        return series

    def rst_material(self, strat, idx):
        """Return the resistence of a given material.

        :param strat (dict): info relative to each index in the pattern
        :param idx (str): position of a given material in the pattern
        :return rst (float): the resistance
        """
        rst = 0
        if "cnd" in strat[idx]:
            rst = strat[idx]["thk"] / strat[idx]["cnd"]  # (m^2 K)/W
        else:
            rst = strat[idx]["rst"]  # (m^2 K)/W
        rst = rst / strat[idx]["area"]  # K/W
        strat[idx]["rst/area"] = "{:.3f}".format(rst)  # 3 deciamls
        return rst


class Latex(Transmittance):
    """Write the LaTex document."""
    def __init__(self, pattern, stratigraphy, area, filename, lang):
        super().__init__(pattern, stratigraphy, area)

        preamble = self.preamble(lang)
        table = self.table()
        with open(filename, "w") as f:
            f.write("\n".join(preamble))
            f.write("\n\\begin{document}\n\n")
            f.write("\n".join(table))
            f.write("\n\n\\end{document}")
            f.closed

    def preamble(self, lang):
        """Preamble.

        :param lang (str): language to use for babel package
        return preamble (list): the preamble
        """
        preamble = ["\\documentclass[10pt,a4paper]{article}",
                    "\\usepackage[utf8]{inputenc}",
                    "\\usepackage[{}]{{babel}}".format(lang),
                    "\\usepackage{amsmath}",
                    "\\usepackage{amsfonts}",
                    "\\usepackage{amssymb}",
                    "\\usepackage{graphicx}",
                    "\\usepackage[left=2cm,right=2cm,"
                    "top=2cm,bottom=2cm]{geometry}",
                    "\\usepackage{caption}",
                    "\\usepackage{siunitx}"]
        return preamble

    def table(self):
        """Table result of the stratigraphy.
        return table (list): the table
        """
        table = ["\\begin{table}[ht]",
                 "\\centering",
                 "\\begin{tabular}{c|ccccc|ccc}",
                 "& "
                 "[m] & "
                 "$\left[\dfrac{W}{(K \cdot m)}\\right]$ & "
                 "$\left[\dfrac{(m^2 \cdot K)}{W}\\right]$ & "
                 "[$m^2$] & "
                 "$\left[\dfrac{K}{W}\\right]$ & "
                 "[$m^2$] & "
                 "$\left[\dfrac{(m^2 \cdot K)}{W}\\right]$ & "
                 "$\left[\dfrac{W}{(m^2 \cdot K)}\\right]$ \\\\",
                 "\\# & "
                 "$s_i$ & "
                 "$\lambda_i$ & "
                 "$R_i$ & "
                 "$A_i$ & "
                 "$R_i/A_i$ & "
                 "$A$ & "
                 "$R$ & "
                 "$K$ \\\\",
                 "\\hline",
                 "\\hline",
                 "\\end{tabular}",
                 "\\end{table}"]
        return table


def test():
    pattern = "1, (2,3,4)//5//(6,7), 8"
    strat = {
        "1": {"mat": 1, "thk": 1, "area": 3, "cnd": .1},
        "2": {"mat": 2, "thk": 1, "area": 1, "rst": .2},
        "3": {"mat": 3, "thk": 1, "area": 1, "cnd": .3},
        "4": {"mat": 2, "thk": 1, "area": 1, "rst": .4},
        "5": {"mat": 4, "thk": 3, "area": 1, "cnd": .5},
        "6": {"mat": 3, "thk": 1.5, "area": 1, "cnd": .6},
        "7": {"mat": 2, "thk": 1.5, "area": 1, "rst": .7},
        "8": {"mat": 1, "thk": 1, "area": 3, "cnd": .8}
    }
    area = 3
    filename = "testThStrat.tex"
    lang = "english"

    Latex(pattern, strat, area, filename, lang)


if __name__ == "__main__":
    test()

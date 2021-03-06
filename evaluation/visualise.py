from optparse import OptionParser
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import json
import re
import csv
from matplotlib import rcParams
import collections

rcParams['font.family'] = 'serif'
rcParams['font.sans-serif'] = ['Palatino']
rcParams['font.serif'] = ['Palatino']
rcParams["font.size"] = "10"
rcParams['text.usetex'] ='false'
rcParams["font.weight"] = "normal" # does not work :/
rcParams["axes.labelweight"] = "normal" # does not work :/
rcParams['figure.dpi'] = "300" 

def main():
    parser = OptionParser()
    parser.add_option( '-i',
                    '--input',
                    dest = 'input',
                    metavar = 'FILE' )
    parser.add_option( '-o',
                    '--output',
                    dest = 'output',
                    metavar = 'FOLDER' )
    (options, _) = parser.parse_args()

    in_path = str(Path(options.input))
    out_path = str(Path(options.output))

    visualise_crawl(in_path, out_path)
    # visualise_evaluation(in_path, out_path)

def visualise_crawl(in_path, out_path):
    with open(in_path, 'r') as f:
        log = json.load(f)

    for dic in log.keys():
        if dic == 'succeeded' or dic == 'failed':
            continue

        # BAR
        xs = [i * 100 for i in list(log[dic].values())[:10]]
        ys = list(log[dic].keys())[:10]

        plt.barh(ys, xs, color='b')

        # plt.title(dic)
        plt.xlabel('Occurences in %')
        plt.ylabel('Attributes')

        plt.tight_layout()

        save_path: str = str(Path(out_path).joinpath('bar').joinpath(dic)) + '.pdf'
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, bbox_inches='tight')
        
        plt.clf()

        # Dots
        if dic == 'font_weight_dict' or dic == 'font_size_dict':
            temp = {}

            for i, (k, v) in enumerate(log[dic].items()):
                if i >= 10:
                    break
                temp[k] = v
            od = collections.OrderedDict(sorted(temp.items()))

            xs = [i * 100 for i in list(od.values())[:10]]
            ys = list(od.keys())[:10]

            plt.plot(ys, xs, 'bo')

            # plt.title(dic)
            plt.xlabel('Attributes')
            plt.ylabel('Occurences in %')

            plt.tight_layout()

            save_path: str = str(Path(out_path).joinpath('dot').joinpath(dic)) + '.pdf'
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, bbox_inches='tight')

            plt.clf()

        # PIE
        # plt.pie(labels=list(log[dic].keys())[:10], x=list(log[dic].values())[:10])
        plt.pie(labels=list(log[dic].keys()), x=list(log[dic].values()))

        # plt.title(dic)
        plt.tight_layout()

        save_path: str = str(Path(out_path).joinpath('pie').joinpath(dic)) + '.pdf'
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, bbox_inches='tight')
        plt.clf()
        # plt.show()

def visualise_evaluation(in_path, out_path):
    # path,tp_l,fp_l,fn_l,tp_d,fp_d,fn_d,time_l,time_d,time_c

    results: [{str: str}] = []
    cp_reg = r'cp(\d+)'
    lp_reg = r'lp(\d+)'
    for path in sorted(Path(in_path).rglob('*.csv')):
        cp: str = re.search(cp_reg, path.name).groups()[0]
        cp = cp[:1] + '.' + cp[1:]
        lp: str = re.search(lp_reg, path.name).groups()[0]
        lp = lp[:1] + '.' + lp[1:]

        tp_l_complete: int = 0
        fp_l_complete: int = 0
        fn_l_complete: int = 0
        t_d_complete: int = 0
        f_d_complete: int = 0
        time_l_complete: int = 0
        time_d_complete: int = 0
        time_c_complete: int = 0
        entries: int = 0

        with open(path) as f:
            reader = csv.reader(f)
            for i, l in enumerate(reader):
                if i > 0:
                    tp_l_complete += int(l[1])
                    fp_l_complete += int(l[2])
                    fn_l_complete += int(l[3])
                    t_d_complete += int(l[4])
                    f_d_complete += int(l[5])
                    time_l_complete += int(l[6])
                    time_d_complete += int(l[7])
                    time_c_complete += int(l[8])
                    entries += 1

        # LOCALISATION
        accuracy_l: float = -1.0
        precision_l: float = -1.0
        recall_l: float = -1.0
        fone_score_l: float = -1.0
        try:
            accuracy_l = (tp_l_complete) / (tp_l_complete + fp_l_complete + fn_l_complete)
        except:
            pass
        try:
            precision_l = (tp_l_complete) / (tp_l_complete + fp_l_complete)
        except:
            pass
        try:
            recall_l = (tp_l_complete) / (tp_l_complete + fn_l_complete)
        except:
            pass
        try:
            fone_score_l =  2 * (precision_l * recall_l) / (precision_l + recall_l)
        except:
            pass

        # DETERMINATION
        precision_d: float = -1.0
        try:
            precision_d = (t_d_complete) / (t_d_complete + f_d_complete)
        except:
            pass

        results.append({'cp': cp, 'lp': lp, 'accuracy_l': accuracy_l, 'precision_l': precision_l, 'recall_l': recall_l, 'fone_score_l': fone_score_l, 'precision_d': precision_d, 'time_l_complete': time_l_complete, 'time_d_complete': time_d_complete, 'entries': entries})


    cps: [str] = sorted(list(set([r['cp'] for r in results])))
    lps: [str] = sorted(list(set([r['lp'] for r in results])))
    # Localisation
    accuracy_ls = np.zeros((len(cps),len(lps)))
    precision_ls = np.zeros((len(cps),len(lps)))
    recall_ls = np.zeros((len(cps),len(lps)))
    fone_score_ls = np.zeros((len(cps),len(lps)))

    accuracy_ll = np.zeros(len(cps))
    precision_ll = np.zeros(len(cps))
    recall_ll = np.zeros(len(cps))
    fone_score_ll = np.zeros(len(cps))

    time_l_complete = 0
    time_d_complete = 0
    entries_complete = 0

    for r in results:
        time_l_complete += r['time_l_complete']
        time_d_complete += r['time_d_complete']
        entries_complete += r['entries']
    time_c_complete = time_l_complete + time_d_complete

    mean_time_l = (time_l_complete / entries_complete) / 1000 / 1000
    mean_time_d = (time_d_complete / entries_complete) / 1000 / 1000
    mean_time_c = (time_c_complete / entries_complete) / 1000 / 1000

    print('mean_time_l (in s): ' + str(mean_time_l))
    print('mean_time_d (in s): ' + str(mean_time_d))
    print('mean_time_c (in s): ' + str(mean_time_c))

    # Determination
    precision_ds = np.zeros((len(cps),len(lps)))
    for i, cp in enumerate(cps):
        for j, lp in enumerate(lps):
            for d in results:
                if d['cp'] == cp and d['lp'] == lp:
                    accuracy_ls[i, j] = d['accuracy_l'] * 100
                    precision_ls[i, j] = d['precision_l'] * 100
                    recall_ls[i, j] = d['recall_l'] * 100
                    fone_score_ls[i, j] = d['fone_score_l'] * 100
                    precision_ds[i, j] = d['precision_d'] * 100

                    accuracy_ll[i] = d['accuracy_l'] * 100
                    precision_ll[i] = d['precision_l'] * 100
                    recall_ll[i] = d['recall_l'] * 100
                    fone_score_ll[i] = d['fone_score_l'] * 100
                    break

    # save_hm(accuracy_ls, 'accuracy_ls', cps, lps, out_path)
    # save_hm(precision_ls, 'precision_ls', cps, lps, out_path)
    # save_hm(recall_ls, 'recall_ls', cps, lps, out_path)
    # save_hm(fone_score_ls, 'fone_score_ls', cps, lps, out_path)

    a_plot, = create_dots(accuracy_ll, 'accuracy_ls', cps, 'r', out_path)
    p_plot, = create_dots(precision_ll, 'precision_ls', cps, 'b', out_path)
    r_plot, = create_dots(recall_ll, 'recall_ls', cps, 'g', out_path)
    f_plot, = create_dots(fone_score_ll, 'fone_score_ls', cps, 'y', out_path)

    plt.legend([a_plot, p_plot, r_plot, f_plot], ['Accuracy', 'Precision', 'Recall', 'F1 Score'])

    save_path = str(Path(out_path).joinpath('determination')) + '.pdf'
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, bbox_inches='tight')
    plt.clf()

    save_hm(precision_ds, 'precision_ds', cps, lps, out_path)


def create_dots(ys, label, xs, color, out_path):

    # plt.axis(ys)

    plt.xlabel('cp')
    plt.ylabel('Result')
    return plt.plot(xs, ys, color + 'o')


def show_hm(values, label, cps, lps):
    fig, ax = plt.subplots()

    im, cbar = heatmap(values, cps, lps, ax=ax,
                    cmap="YlGn", cbarlabel=(label + ' in %'))
    texts = annotate_heatmap(im, valfmt="{x:.2f}%")

    fig.tight_layout()
    plt.show()
    # plt.clf()

def save_hm(values, label, cps, lps, out_path):
    fig, ax = plt.subplots()
    plt.xlabel("lp")
    plt.ylabel("cp")

    im, cbar = heatmap(values, cps, lps, ax=ax,
                    cmap="YlGn", cbarlabel=(label + ' in %'))
    texts = annotate_heatmap(im, valfmt="{x:.2f}%")

    fig.tight_layout()

    save_path = str(Path(out_path).joinpath(label)) + '.pdf'
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, bbox_inches='tight')

def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on bottom.
    ax.tick_params(top=False, bottom=True,
                   labeltop=False, labelbottom=True)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar

def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=["black", "white"],
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A list or array of two color specifications.  The first is used for
        values below a threshold, the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts


if __name__ == '__main__':
    main()

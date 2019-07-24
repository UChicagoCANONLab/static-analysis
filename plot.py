# By Marco Anaya


# python3 plot.py (module)

import sys
import os
import math
import string

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_pdf import PdfPages

# supports coloring 12 categories, repeating once until 24
colors = dict(zip(string.ascii_uppercase,
            ['#E58606', '#5D69B1', '#52BCA3', '#99C945', '#CC61B0', '#24796C', 
            '#DAA51B', '#2F8AC4', '#764E9F', '#ED645A', '#CC3A8E', '#A5AA99',
            '#E58606', '#5D69B1', '#52BCA3', '#99C945', '#CC61B0', '#24796C', 
            '#DAA51B', '#2F8AC4', '#764E9F', '#ED645A', '#CC3A8E', '#A5AA99',
            '#E58606', '#5D69B1', '#52BCA3']))

module = sys.argv[1]
module += '' if module[-1] == '/' else '/'
modname = module.strip('/')
path = module + 'csv/'

min_size = 5

class_perf = pd.read_csv(path + modname + '_class_performance_per_req.csv')
class_distr = pd.read_csv(path + modname + '_class_distributions.csv')
class_perf = class_perf[class_perf['Class Size'] > min_size]
class_distr = class_distr[class_distr['Class Size'] > min_size]


def main():
    grades = list(filter(lambda entry: os.path.isdir(path + entry), os.listdir(path)))
    print('Graphing ' + modname + ':')
    for grade in grades:
        print('  performance and distribution graphs for grade ' + str(grade))
        plot_grade(grade)    

    print('  performance by classroom and grade')
    plot_module(grades)


def plot_grade(grade):
    df = class_perf
    df2 = class_distr
    pdf = PdfPages(module + 'graphs/' + modname + '-' + grade + '.pdf')

    df = df.loc[df['Grade'] == int(grade)]
    by_req_data = df.iloc[:, 4:len(df.columns) - 2]
    tIDs = list(df['Teacher ID'])
    cIDs = list(df['Studio ID'])
    class_sizes = list(df.iloc[:, 3])

    # construct per-requirement graph
    plt.subplots(figsize=(10, 6))
    plt.title((modname + ' grade ' + grade + ' Classroom Performance Per Requirement').title())

    req_count = len(by_req_data.columns)
    class_count = len(by_req_data.index)
    pos = list(range(req_count))
    width = .7 / (class_count)

    labels = [tID + '-' + str(cID) + ' (n=' + str(class_size) + ')' for (tID, cID, class_size) in zip(tIDs, cIDs, class_sizes)]
    
    # plotting a set of bars for each grade level
    for i, (index, row) in enumerate(by_req_data.iterrows()):
        plt.bar(pos if i == 0 else [p + width * i for p in pos],
            row,
            width * .9,
            alpha=0.7,
            color=colors[tIDs[i]],
            label=labels[i],
            zorder=3)
    plt.xlabel('Requirements')
    plt.xticks([p + (width * .9 * class_count / 2) for p in pos], labels=[p + 1 for p in pos])
    plt.ylabel('Percent Complete')
    plt.ylim([0, 100])
    plt.grid(axis='y', zorder=0, which='both')
    plt.legend(bbox_to_anchor=(1.04, 1), loc='upper right', ncol=1)

    plt.savefig(module + 'graphs/pngs/' + modname + '-' + grade + '-per-req.png', bbox_inches='tight')
    pdf.savefig(bbox_inches='tight')

    # construct totals graph
    if class_count > 1:
        total_data = df['Total']
        plt.subplots(figsize=(10, 6))
        plt.title((modname + ' grade ' + grade + ' Classroom Performance Totals').title())
        plt.bar(
            list(range(class_count)),
            total_data,
            alpha=0.7,
            color=[colors[tID] for tID in tIDs],
            zorder=3
        )
        plt.xlabel('Classroom')
        plt.xticks(list(range(class_count)), labels=labels, rotation=20, horizontalalignment='right')
        plt.ylabel('Percent Complete')
        plt.ylim([0, 100])
        plt.grid(axis='y', zorder=0, which='both')

        plt.savefig(module + 'graphs/pngs/' + modname + '-' + grade + '-totals.png', bbox_inches='tight')
        pdf.savefig(bbox_inches='tight')

    df2 = df2.loc[df2['Grade'] == int(grade)]
    distr_data = df2.iloc[:, 4:]

    # construct distribution graph
    fig, axs = plt.subplots(math.ceil(class_count / 2), 2, figsize=(10, 5 * math.ceil(class_count / 2)))
    
    for i, (ax, (index, row)) in enumerate(zip(axs.reshape(-1), distr_data.iterrows())):
        pos = list(distr_data.columns)
        ax.bar(pos, row, .95,
            alpha=0.7, zorder=3, color=colors[tIDs[i]])

        if class_count > 1:
            ax.set_title(('Classroom ' + str(cIDs[i])).title())
        else:
            ax.set_title(('Classroom ' + str(cIDs[i]) + ' Distribution').title())

        ax.set_xlabel('Score')
        ax.set_xticks(pos)
        ax.set_xticklabels = row.index

        ax.set_ylabel('Students')
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        ax.grid(axis='y', zorder=0, which='major', alpha=0.5)

    if class_count % 2 != 0:
        axs.reshape(-1)[-1].remove()
    if class_count > 1:
        fig.suptitle('Grade Distributions')

    plt.savefig(module + 'graphs/pngs/' + modname + '-' + grade + '-distributions.png', bbox_inches='tight')
    pdf.savefig(bbox_inches='tight')

    pdf.close()


def plot_module(grades):
    df = class_perf
    totals_data = [df.loc[df['Grade'] == int(grade)] for grade in grades]

    # construct graph measuring performance by classroom and grade
    fig, axs = plt.subplots(1, len(grades), sharey=True, sharex=True, figsize=(3 * len(grades), 6))
    fig.suptitle((modname + ' Requirement Completion by Classroom and Grade').title())
    fig.text(0.5, 0.05, 'Grades', ha='center', va='center')
    fig.text(0.08, 0.5, 'Classroom Completion (%)', ha='center', va='center', rotation='vertical')

    for i, [d, ax] in enumerate(zip(totals_data, axs)):
        bars = len(d.index)
        labels = [list(d['Teacher ID'])[i] + '-' + str(list(d['Studio ID'])[i]) + ' (n=' + str(list(d.iloc[:, 3])[i]) + ')' for i in range(bars)]
        bar = ax.bar(
            list(range(bars)),
            d['Total'],
            .9,
            color=[colors[tID] for tID in list(d['Teacher ID'])],
            alpha=0.7,
            zorder=3
        )
        ax.set_ylim([0, 100])
        ax.set_xlabel(grades[i])
        ax.tick_params(labelbottom=False)
        ax.legend(bar, labels, bbox_to_anchor=(1, -0.1), loc='upper right', ncol=1)

    plt.savefig(module + 'graphs/pngs/' + modname + '-by-classroom.png', bbox_inches='tight')
    plt.savefig(module + 'graphs/' + modname + '-teacher-analysis.pdf', bbox_inches='tight')


if __name__ == '__main__':
    main()

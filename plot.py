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

min_size = 5


def plot(project, module, class_distributions=None, class_performance_per_req=None):
    class_perf, class_distr = class_performance_per_req, class_distributions

    csv_path = "./" + project + "/" + module + '/csv/'
    graph_path = "./" + project + "/" + module + '/graphs/'
    if class_perf is None:
        class_perf = pd.read_csv(csv_path + module + '_class_performance_per_req.csv')
    if class_distr is None:
        class_distr = pd.read_csv(csv_path + module + '_class_distributions.csv')
    
    
    class_perf = class_perf[class_perf['Class Size'] > min_size]
    class_distr = class_distr[class_distr['Class Size'] > min_size]

    # Runs plot_grade() for each grade level, generating three graphs
    grades = list(filter(lambda entry: os.path.isdir(csv_path + entry), os.listdir(csv_path)))
    print('Graphing ' + module + ':')
    for grade in grades:
       
        plot_grade(graph_path, module, grade, class_perf, class_distr)    
        print('  performance and distribution graphs for grade ' + str(grade) + '.')

    # Generates teacher analysis for the whole module
    plot_module(graph_path, module, grades, class_perf)
    print('  performance by classroom and grade.')
    print('Done.')


def plot_grade(path, module, grade, class_perf, class_distr):
    df = class_perf
    df2 = class_distr

    pdf = PdfPages(path + module + '-' + grade + '.pdf')

    df = df.loc[df['Grade'] == grade]

    by_req_data = df.iloc[:, 4:len(df.columns) - 1]

    tIDs = list(df['Teacher ID'])
    cIDs = list(df['Studio ID'])
    class_sizes = list(df.iloc[:, 3])

    # construct per-requirement graph
    plt.subplots(figsize=(10, 6))
    plt.title((module + ' grade ' + grade + ' Classroom Performance Per Requirement').title())

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

    plt.savefig(path + 'pngs/' + module + '-' + grade + '-per-req.png', bbox_inches='tight')
    pdf.savefig(bbox_inches='tight')
    plt.close()

    # construct totals graph
    if class_count > 1:
        total_data = df['Total']
        plt.subplots(figsize=(10, 6))
        plt.title((module + ' grade ' + grade + ' Classroom Performance Totals').title())
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

        plt.savefig(path + 'pngs/' + module + '-' + grade + '-totals.png', bbox_inches='tight')
        pdf.savefig(bbox_inches='tight')
        plt.close()

    df2 = df2.loc[df2['Grade'] == grade]
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

    plt.savefig(path + 'pngs/' + module + '-' + grade + '-distributions.png', bbox_inches='tight')
    pdf.savefig(bbox_inches='tight')

    pdf.close()
    plt.close()

# plots teacher analysis using TOTALS column from CLASS PERFORMANCE PER REQUIREMENT
def plot_module(path, module, grades, class_perf):
    df = class_perf
    totals_data = [df.loc[df['Grade'] == grade] for grade in grades]

    # construct graph measuring performance by classroom and grade
    fig, axs = plt.subplots(1, len(grades), sharey=True, sharex=True, figsize=(3 * len(grades), 6))
    fig.suptitle((module + ' Requirement Completion by Classroom and Grade').title())
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

    plt.savefig(path + 'pngs/' + module + '-by-classroom.png', bbox_inches='tight')
    plt.savefig(path + module + '-teacher-analysis.pdf', bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    plot(sys.argv[1], sys.argv[2])

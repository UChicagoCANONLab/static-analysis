# By Marco Anaya, based on code from Zack Crenshaw


# python3 plotGrades.py (module)

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

data_by_tID = {}
by_cID_data = []
grade_teacher_data = []
per_student_data = []
distr_data = []

def plot_grade(module, grade_dir):

    modname = module.split('/')[1]
    grade = grade_dir.split('/')[-2]

    # initializing the post-processed data for each of the 3 graphs
    by_reqs_data = []
    totals_data = pd.Series()
    
    

    IDs = []
    # initial data manipulation for each csv (studio) in grade folder
    for filename in os.listdir(grade_dir):
        if not filename.endswith(".csv"):
            continue
        path = grade_dir + filename

        class_data = pd.read_csv(path).drop(['Error grading project'], axis=1)

        student_count = len(class_data.index)
        req_count = len(class_data.columns) - 1

        # make sure class size is of a certain size
        min_size = 5
        if student_count < min_size:
            continue
        
        ID = filename.split('.')[0] + ' (n=' + str(student_count) + ')'
        IDs.append(ID)
        tID = ID.split('-')[0]
        class_info = {
            "Grade": grade, 
            "Teacher ID": tID, 
            "Studio ID": ID.split('-')[1].split()[0],
            "Class Size (classes with less than " + str(min_size) + " student(s) were excluded)": student_count
        }
        # data for percentage of completion by class by requirement with totals on last column
        possible_score = student_count * req_count
        score_totals = class_data.drop('ID', axis=1).sum(axis=0)
        by_reqs_row = {
            **class_info,
            **(100 * score_totals / student_count).round(0).to_dict(),
            **{'Total': (score_totals.sum() * 100 / possible_score).round(0)}
        }             
        print(by_reqs_row)
        by_reqs_data.append(by_reqs_row)
        
        # data for distributions by class
        distr_row = pd.concat([class_data, pd.DataFrame(class_data.sum(axis=1), columns=['Sum'])], axis=1) \
            .groupby('Sum').Sum.count() \
            .reindex(range(req_count + 1), fill_value=0).to_dict()
        print({**class_info, **distr_row})
        distr_data.append({**class_info, **distr_row})

        data_by_tID[tID] = data_by_tID[tID].append(class_data) if tID in data_by_tID.keys() else class_data
        
        grade_teacher_data.append({**class_info, **{
            "Student Count": student_count,
            "Class Completion": (score_totals.sum() * 100 / possible_score).round(0)
        }})
        print(grade_teacher_data)

        for (i, val) in class_data.sum(axis=1, numeric_only=True).iteritems():
            per_student_data.append({**class_info, **{
                "Student ID": class_data.at[i, 'ID'],
                "Score": val,
                "Out of": req_count,
                "Percentage": val / req_count
            }})
        print(per_student_data)
        
        sys.exit()


    # defining pdf where graphs for each class will be joined
    pdf = PdfPages(module + 'graphs/' + modname + '-' + grade + '.pdf')

    # construct per-requirement graph
    plt.subplots(figsize=(10, 6))
    plt.title((modname + ' grade ' + grade + ' Classroom Performance Per Requirement').title())

    pos = list(range(len(by_reqs_data.index)))
    width = .7 / (len(IDs))



    # plotting a set of bars for each grade level
    for i, class_id in enumerate(IDs):
        if 'Requirement' not in class_id:
            plt.bar(
                pos if i == 0 else [p + width * i for p in pos],
                by_reqs_data[class_id],
                width * .9,
                alpha=0.7,
                color=colors[class_id.split('-')[0]],
                label=class_id,
                zorder=3
            )
    plt.xlabel('Requirements')
    plt.xticks([p + (width * .9 * len(IDs) / 2)  for p in pos], labels=[p + 1 for p in pos])
    plt.ylabel('Percent Complete') 
    plt.ylim([0, 100])
    plt.grid(axis='y', zorder=0, which='both')
    plt.legend(bbox_to_anchor=(1.04, 1), loc='upper right', ncol=1)

    plt.savefig(module + 'graphs/pngs/' + modname + '-' + grade + '-per-req.png', bbox_inches='tight')
    pdf.savefig(bbox_inches='tight')


    # construct totals graph
    if len(IDs) > 1:
        plt.subplots(figsize=(10, 6))
        plt.title((modname + ' grade ' + grade + ' Classroom Performance Totals').title())
        plt.bar(
            list(range(len(IDs))),
            totals_data,
            alpha=0.7,
            color=[colors[ID.split('-')[0]] for ID in IDs],
            zorder=3
        )
        plt.xlabel('Classroom')
        plt.xticks(list(range(len(IDs))), labels=IDs, rotation=20, horizontalalignment='right')
        plt.ylabel('Percent Complete')
        plt.ylim([0, 100])
        plt.grid(axis='y', zorder=0, which='both')

        plt.savefig(module + 'graphs/pngs/' + modname + '-' + grade + '-totals.png', bbox_inches='tight')
        pdf.savefig(bbox_inches='tight')

    # construct distribution graph
    fig, axs = plt.subplots(math.ceil(len(distr_data) / 2), 2, figsize=(10, 5 * math.ceil(len(distr_data) / 2)))
    fig.suptitle('Grade Distributions')
    for i, [ax, d] in enumerate(zip(axs.reshape(-1), distr_data + [0])):
        if i < len(IDs):
            pos = list(range(len(d.index)))
            ax.bar(
                pos,
                d,
                .95,
                alpha=0.7,
                zorder=3,
                color=colors[IDs[i].split('-')[0]]
            )
            ax.set_title(('Classroom ' + d.name).title())

            ax.set_xlabel('Score')
            ax.set_xticks(pos)
            ax.set_xticklabels = d.index

            ax.set_ylabel('Students')
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))

            ax.grid(axis='y', zorder=0, which='major', alpha=0.5)

        else:
            ax.remove()  # remove the possible extra subplot

    plt.savefig(module + 'graphs/pngs/' + modname + '-' + grade + '-distributions.png', bbox_inches='tight')
    pdf.savefig(bbox_inches='tight')

    pdf.close()


def main():
    module = sys.argv[1]
    module += '' if module[-1] == '/' else '/'
    modname = module.split('/')[1]

    grades = []
    for entry in os.listdir(module + 'csv/'):
        if not os.path.isdir(module + 'csv/' + entry) or 'aggregated' in entry:
            continue

        grade_dir = module + 'csv/' + entry + '/'
        plot_grade(module, grade_dir)

        grades.append(entry)
    
    # final data manipulation across a whole module

    pd.DataFrame(per_student_data).to_csv(module + 'csv/aggregated/' + modname + '-completion_by_student.csv', index=False, columns=["Grade", 
                "Teacher ID",
                "Studio ID",
                "Score",
                "Out of",
                "Percentage"])
    pd.DataFrame(grade_teacher_data).to_csv(module + 'csv/aggregated/' + modname + '-completion_by_teacher_and_grade.csv', index=False, columns=["Grade", "Teacher ID", "Studio ID", "Class Completion"])

    data5 = pd.Series()
    for tID, df in data_by_tID.items():
        aggr = df.sum(axis=0).sum() * 100 / (len(df.columns) * len(df.index))
        data5 = data5.append(pd.Series(aggr, index=[tID]))

    pdf = PdfPages(module + 'graphs/' + modname + '-teacher-analysis.pdf')

    # construct graph measuring performance by classroom and grade
    fig, axs = plt.subplots(1, len(by_cID_data), sharey=True, sharex=True, figsize=(3 * len(by_cID_data), 6))
    fig.suptitle((modname + ' Requirement Completion by Classroom and Grade').title())
    fig.text(0.5, 0.05, 'Grades', ha='center', va='center')
    fig.text(0.08, 0.5, 'Classroom Completion (%)', ha='center', va='center', rotation='vertical')

    for i, [d, ax] in enumerate(zip(by_cID_data, axs)):
        bar = ax.bar(
            list(range(len(d.index))),
            d,
            .9,
            color=[colors[ID.split('-')[0]] for ID in d.index],
            alpha=0.7,
            zorder=3
        )
        ax.set_ylim([0, 100])
        ax.set_xlabel(grades[i])
        ax.tick_params(labelbottom=False)
        ax.legend(bar, d.index, bbox_to_anchor=(1, -0.1), loc='upper right', ncol=1)

    plt.savefig(module + 'graphs/pngs/' + modname + '-by-classroom.png', bbox_inches='tight')
    pdf.savefig(bbox_inches='tight')

    # construct graph measuring performance by teacher
    plt.subplots(figsize=(10, 6))
    plt.title((modname + ' Requirement Completion by Teacher').title())
    plt.bar(
        list(range(len(data5))),
        data5,
        alpha=0.7,
        color=[colors[tID] for tID in data5.keys()],
        zorder=3
    )
    plt.xlabel('Teacher')
    plt.xticks(list(range(len(data5.keys()))), labels=data5.keys())
    plt.ylabel('Percent Complete')
    plt.ylim([0, 100])
    plt.grid(axis='y', zorder=0, which='both')

    plt.savefig(module + 'graphs/pngs/'+ modname + '-by-teacher.png', bbox_inches='tight')
    pdf.savefig(bbox_inches='tight')

    pdf.close()

if __name__ == '__main__':
    main()

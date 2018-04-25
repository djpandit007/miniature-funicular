from flask import Flask, render_template, jsonify, make_response, request
from subprocess import call
import sqlite3
import json

import networkx as nx
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def writeClingoInputData():
    conn = sqlite3.connect("project.db")

    scores = conn.execute("SELECT ID, SCORE FROM LEARNERS").fetchall()
    with open("data", "w") as a_file:
        for score in scores:
            a_file.write("studentScore(%s, %s).\n" % (score[0], score[1]))
        num_groups = len(scores) / 3
        for num in range(1, num_groups + 1):
            a_file.write("group(%s).\n" % (num))

def writeActionInputData(inputFile):
    edges = []
    with open("topicDependency", "w") as a_file:
        with open(inputFile) as f:
            for line in f:
                line = line.split(":")
                line0 = line[0].strip()
                line1 = line[1].strip().split(",")
                if line1 != [""]:
                    for topic in line1:
                        a_file.write("learnAfter(t%s,t%s).\n" % (line0, topic.strip()))
                        edges.append(("t" + topic.strip(), "t" + line0))
    return edges

def writeQueryData(expertise):
    expertise = expertise.split(",")
    print "Learner Expertise: ", expertise
    with open("query", "w") as a_file:
        a_file.write(":- query\n")
        a_file.write("maxstep :: 1..20;\n")
        a_file.write("0: ")
        for num in range(1, 11):
            topicNum = "t" + str(num)
            if topicNum in expertise:
                a_file.write("knows(%s) " % topicNum)
            else:
                a_file.write("~knows(%s) " % topicNum)
            if num != 10:
                a_file.write(" & ")
        a_file.write(";\nmaxstep: knows(t1) & knows(t2) & knows(t3) & knows(t4) & knows(t5) & knows(t6) & knows(t7) & knows(t8) & knows(t9) & knows(t10).")

@app.route("/", methods=["GET", "POST"])
def landing():
    conn = sqlite3.connect("project.db")

    if request.method == "POST":
        params = request.form
        paramString = ""
        for p in params:
            if "t" in p:
                paramString += p + ","
            else:
                identifier = p
        paramString = paramString[:-1]

        with conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE LEARNERS SET EXPERTISE=\"%s\" WHERE ID=%s" % (paramString, identifier))

    cursor = conn.execute("SELECT id, name from LEARNERS")
    return render_template("dashboard.html", result=cursor)

@app.route("/similar")
def similar():
    groupDict = {}
    writeClingoInputData()
    outputFile = open("similar_groupify_output.txt", "w")
    call(["clingo", "similar_groupify", "data", "--verbose=0"], stdout=outputFile)
    outputFile.close()
    readFile = open("similar_groupify_output.txt", "r")
    answer = readFile.readline().strip().split(" ")
    readFile.close()

    conn = sqlite3.connect("project.db")
    for ans in answer:
        group, identity, score = ans.split(",")
        group, identity, score = int(group[-1]), int(identity), int(score[:-1])
        name = conn.execute("SELECT NAME FROM LEARNERS WHERE ID=%s" % (str(identity)))
        if int(group) in groupDict:
            groupDict[group].append((name.fetchone()[0].encode("ascii"), score))
        else:
            groupDict[group] = [(name.fetchone()[0].encode("ascii"), score)]

    return render_template("groupify.html", result=groupDict, strategy="Similar")

@app.route("/dissimilar")
def dissimilar():
    groupDict = {}
    writeClingoInputData()
    outputFile = open("dissimilar_groupify_output.txt", "w")
    call(["clingo", "dissimilar_groupify", "data", "--verbose=0"], stdout=outputFile)
    outputFile.close()
    readFile = open("dissimilar_groupify_output.txt", "r")
    answer = readFile.readline().strip().split(" ")
    readFile.close()

    conn = sqlite3.connect("project.db")
    for ans in answer:
        group, identity, score = ans.split(",")
        group, identity, score = int(group[-1]), int(identity), int(score[:-1])
        name = conn.execute("SELECT NAME FROM LEARNERS WHERE ID=%s" % (str(identity)))
        if int(group) in groupDict:
            groupDict[group].append((name.fetchone()[0].encode("ascii"), score))
        else:
            groupDict[group] = [(name.fetchone()[0].encode("ascii"), score)]

    return render_template("groupify.html", result=groupDict, strategy="Dissimilar")

@app.route("/progress", methods=["POST"])
def progress():
    conn = sqlite3.connect("project.db")
    studentID = request.form.get("progress")
    name = conn.execute("SELECT NAME FROM LEARNERS WHERE ID=%s" % (studentID)).fetchone()

    call(["/home/djpandit/Downloads/alchemy/bin/learnwts", "-i", "progress.mln", "-o", "weights_learned.mln", "-t", "attempts.db", "-ne", "Outcome", "-dMaxSec", "10"])
    with open("weights_learned.mln", "r") as f:
        content = f.readlines()
    content = content[3:-4]
    content = filter(lambda x: "//" not in x and x != "\n", content)
    weights = map(lambda x: float(x.split(" ")[0]), content)
    saveHistogram(weights)
    return render_template("progress.html", student=name[0], weights=weights)

@app.route("/find-path", methods=["POST"])
def find_path():
    conn = sqlite3.connect("project.db")

    graphEdges = writeActionInputData("dependencies.txt")

    studentID = request.form.get("path-student")
    expertise = conn.execute("SELECT EXPERTISE FROM LEARNERS WHERE ID=%s" % (studentID)).fetchone()
    name = conn.execute("SELECT NAME FROM LEARNERS WHERE ID=%s" % (studentID)).fetchone()
    writeQueryData(expertise[0])

    outputFile = open("learning_steps.txt", "w")
    call(["cplus2asp", "adaptiveSystem", "topicDependency", "query", "--query=0", "3"], stdout=outputFile)
    outputFile.close()

    with open("learning_steps.txt") as f:
        content = f.readlines()
    content = map(lambda x: x.strip(), content)
    actions = filter(lambda x: "ACTIONS: " in x or "Solution: " in x, content)
    actions = map(lambda x: x.replace("ACTIONS: ", ""), actions)
    actions = map(lambda x: x.replace(" study(", ""), actions)
    actions = map(lambda x: x.replace(")", ""), actions)

    allSolutions = [[] for num in range(3)]
    solNum = -1
    for action in actions:
        if "Solution: " in action:
            solNum += 1
        else:
            allSolutions[solNum].append(action)

    saveFigure(graphEdges, expertise[0], allSolutions[0], "plan1")
    saveFigure(graphEdges, expertise[0], allSolutions[1], "plan2")
    saveFigure(graphEdges, expertise[0], allSolutions[2], "plan3")
    plan1 = ", ".join(allSolutions[0])
    plan2 = ", ".join(allSolutions[1])
    plan3 = ", ".join(allSolutions[2])
    return render_template("findPath.html", plan1=plan1, plan2=plan2, plan3=plan3, student=name[0])

@app.route("/admin", methods=["POST"])
def admin():
    conn = sqlite3.connect("project.db")
    studentID = request.form.get("admin")
    name = conn.execute("SELECT NAME FROM LEARNERS WHERE ID=%s" % (studentID)).fetchone()
    expertise = conn.execute("SELECT EXPERTISE FROM LEARNERS WHERE ID=%s" % (studentID)).fetchone()
    expertise = expertise[0]
    expertise = expertise.split(",")
    expertise = map(lambda x: int(x.replace("t", "")), expertise)
    print "Name of student: ", studentID, name, expertise
    return render_template("admin.html", student=name[0], expertise=expertise, studentID=studentID)

def saveHistogram(dataPoints):
    plt.clf()
    plt.plot(range(1, len(dataPoints) + 1), dataPoints, marker='o', color='g')
    plt.plot(range(1, len(dataPoints) + 1), [0] * len(dataPoints), color='black', linewidth=2.0)
    plt.title('Current Performance', loc='center')
    plt.xlabel('Topic Number')
    plt.ylabel('Weights')
    plt.grid()

    plt.savefig("./static/images/weights_histogram.png", format="PNG")

def saveFigure(Edges, initKnowledge, actions, outputFile):
    plt.clf()
    initConfig = nx.DiGraph()
    initKnowledge = initKnowledge.split(",")

    initConfig.add_edges_from(Edges)
    # pos = nx.spring_layout(initConfig, k=10.0)
    pos = nx.shell_layout(initConfig)
    black_edges = [edge for edge in Edges]

    nx.draw_networkx_nodes(initConfig, pos, node_color='#C0C0C0')
    nx.draw_networkx_labels(initConfig, pos)
    nx.draw_networkx_nodes(initConfig, pos, nodelist=initKnowledge, node_color='#00FF00')
    nx.draw_networkx_edges(initConfig, pos, edgelist=black_edges, edge_color='black', arrows=True)
    plt.suptitle("Initial Knowledge: " + ", ".join(initKnowledge))

    plt.axis("off")
    plt.savefig("./static/images/" + outputFile + "-1.png", format="PNG")
    plt.clf()

    finalConfig = nx.DiGraph()
    finalConfig.add_edges_from(Edges)
    pos = nx.shell_layout(finalConfig)

    learnOrder = []
    edgeLabels = {}
    for action in actions:
        edge = filter(lambda x: x[1] == action, Edges)
        if edge:
            learnOrder.append(edge[0])

    for order in range(len(learnOrder)):
        edgeLabels[learnOrder[order]] = str(order + 1)

    finalKnowledge = ['t1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 't10']
    # pos = nx.spring_layout(finalConfig, k=10.0)
    black_edges = [edge for edge in Edges if edge not in learnOrder]
    nx.draw_networkx_nodes(finalConfig, pos, node_color='#C0C0C0')
    nx.draw_networkx_labels(finalConfig, pos)
    nx.draw_networkx_nodes(finalConfig, pos, nodelist=finalKnowledge, node_color='#00FF00')
    nx.draw_networkx_edges(finalConfig, pos, edgelist=learnOrder, edge_color='#FFDF00', arrows=True)
    nx.draw_networkx_edges(finalConfig, pos, edgelist=black_edges, edge_color='black', arrows=True)
    nx.draw_networkx_edge_labels(finalConfig, pos, edge_labels=edgeLabels)
    plt.suptitle("Proposed Path")
    plt.figtext(0.25, 0.05, "Learning Order: " + ", ".join(actions), fontsize=12)
    plt.axis("off")
    plt.savefig("./static/images/" + outputFile + "-2.png", format="PNG")
    # animate()

def animate():
    import networkx as nx
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.pyplot import pause
    import pylab
    pylab.ion()
    plt.clf()

    Graph = nx.DiGraph()
    labels = {'t1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 't10'}
    initPosition = {
    't1': [ 0.62595554,  0.21395259],
    't2': [ 1.0,  0.59112415],
    't3': [ 0.0547307,  0.53207903 ],
    't4': [ 0.57086641,  0.53207903],
    't5': [ 0.34546013,  0.30230591],
    't6': [ 0.0547307 ,  0.75364438],
    't7': [ 0.57086641,  0.99915934],
    't8': [ 0.87557846,  0.84131369],
    't9': [ 0.30929179,  0.97162183],
    't10': [ 0.8467943 ,  0.21395259]
    }

    Edges = [
    ('t1', 't4'),
    ('t2', 't4'),
    ('t3', 't5'),
    ('t4', 't5'),
    ('t4', 't6'),
    ('t4', 't7'),
    ('t5', 't7'),
    ('t6', 't8'),
    ('t7', 't8'),
    ('t8', 't9'),
    ('t7', 't10'),
    ('t9', 't10')
    ]

    red_edges = [('t1', 't4'), ('t3', 't5'), ('t4', 't6'), ('t4', 't7'), ('t6', 't8'), ('t8', 't9'), ('t7', 't10')]
    black_edges = [('t2', 't4'), ('t4', 't5'), ('t5', 't7'), ('t7', 't8'), ('t9', 't10')]

    Graph.add_edges_from(Edges)
    currentNode = ['t1', 't2', 't3']
    pos = nx.spring_layout(Graph, pos = initPosition, fixed = labels)
    black_nodes = [edge[1] for edge in Graph.edges() if edge[1] not in currentNode]
    nx.draw_networkx_nodes(Graph,pos, node_color='#C0C0C0')
    nx.draw_networkx_nodes(Graph,pos, nodelist=currentNode, node_color='#00FF00')
    nx.draw_networkx_labels(Graph,pos)
    nx.draw_networkx_edges(Graph, pos, edgelist=black_edges,edge_color='black', arrows=True)
    plt.axis("off")
    pylab.show()

    currentList = []
    def get_fig(i):
        print "Edge: ", red_edges[i]
        currentList.append(red_edges[i])
        currentNode.append(red_edges[i][1])
        pos = nx.spring_layout(Graph, pos = initPosition, fixed = labels)
        black_edges = [edge for edge in Graph.edges() if edge != red_edges[i]]
        black_nodes = [label for label in labels if label not in currentNode]
        nx.draw_networkx_labels(Graph,pos)
        nx.draw_networkx_nodes(Graph,pos, nodelist=currentNode, node_color='#7CFC00')
        nx.draw_networkx_nodes(Graph,pos, nodelist=black_nodes, node_color='#FF8C00')
        nx.draw_networkx_edges(Graph, pos, edgelist=currentList, edge_color='#FFDF00', arrows=True)
        nx.draw_networkx_edges(Graph, pos, edgelist=black_edges,edge_color='black', arrows=True)
        plt.text(0.05, 0.05, "Learning Order: " + ", ".join(currentNode), fontsize=12)

        pylab.show()

    for i in range(len(red_edges)):
        get_fig(i)
        pylab.draw()
        pause(1)
    plt.close()

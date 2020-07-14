# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 11:03:29 2019

@author: mjhoe
"""

import os

import json

import time

import subprocess

import pandas as pd

def is_number_like(x):
    try:
        int(x)
        return True
    except (TypeError, ValueError):
        try:
            float(x)
            return True
        except (TypeError, ValueError):
            return False

def update_dict(section, year, count):
    if section not in cv.keys():
        cv[section] = {}
    
    if year not in cv[section].keys():
        cv[section][year] = count
    else:
        cv[section][year] += count
        
        

def get_satisfier_need_info(satisfier, need):
    print("On a scale of 1-3 (1=bad, 2=neutral, 3=good), how good do you feel about using", satisfier,"to meet your need for", need + "?")
    affect = input(">")
    print("From 0-100, what percent of your need for", need, "is met by", satisfier + "?")
    satisfaction = input(">")
    
    return {'affect': affect, 'satisfaction_contrib': satisfaction}
    
def get_need_info(need):
    print("On a scale of 0-100, what percent of your need for", need," do you think is currently being met, on average?")
    satisfaction = input(">")
    return satisfaction
    
def get_satisfier_info(satisfier):
    print("On a scale of 1-4 (4=daily, 3=weekly, 2=monthly, 1=rarely), how often do you", satisfier + "?")
    frequency = input(">")
    return frequency
    


schemas = pd.read_csv('schemas.csv')

schema_names = schemas.Schema.unique()

print("Press a number corresponding to the schema you'd like to be surveyed on")

for i, schema in enumerate(schema_names):
    print (i, "=> ", schema)
    
curr_input = input ("choice:")

if not is_number_like(curr_input):
    print("You must enter a number. Goodbye")
else:
    curr_input = int(curr_input)

if curr_input < 0 or curr_input > len(schema_names):
    print("This schema does not exist. Goodbye.")
    
selected_schema = schema_names[int(curr_input)]

print("Schema selected ==>", selected_schema)
print("We'll begin by presenting needs, and asking you how you satisfy them.")
print("After each need is presented, enter an activity you engage in to fulfill that need. \
      You will be asked additional questions about the satisfier.")

print("Press n to move on to the next need.")


selected_needs = schemas[schemas.Schema == selected_schema]


satisfiers = []
edges = []
needs = []

satisfier_ids = []


# the way in which the data is collected sort of determines what the data actually means. 

# TODO: survey should capture the parent category of need

for row in selected_needs.iterrows():
    new_need = {}
    
    print("Getting info about this need:", row[1]['Need'])
    new_need['name'] = row[1]['Need']
    new_need['category'] = row[1]['Category']
    new_need['percent_satisfied'] = get_need_info(row[1]['Need'])
    
    needs.append(new_need)
    
    curr_input = ""
    
    print ("How do you satisfy your need for " + str(row[1]['Need']) + "?")
    new_satisfier = {}
    
    curr_input = input(">")
    new_satisfier['satisfier_label'] = curr_input
    
    while curr_input != 'n':
        if curr_input == 'q':
            print("Exiting")
            exit()
        if new_satisfier['satisfier_label'] not in satisfier_ids:
            print("New satisfier - getting info on it")
            new_satisfier['frequency'] = get_satisfier_info(new_satisfier['satisfier_label'])
            satisfiers.append(new_satisfier)
            satisfier_ids.append(new_satisfier['satisfier_label'])
        else:
            print("Repeat satisfier!")
            
        print("Getting info on the need-satisfier relationship")
        sat_info = get_satisfier_need_info(new_satisfier['satisfier_label'], row[1]['Need'])
        
        sat_info['need_id'] = row[1]['Need']
        sat_info['satisfier_id'] = new_satisfier['satisfier_label']
        
        edges.append(sat_info)
        
        print ("How do you satisfy your need for " + str(row[1]['Need']) + "? (press 'n' to go to the next need)")
        new_satisfier = {}
        curr_input = input(">")
        new_satisfier['satisfier_label'] = curr_input


need_net = {}
need_net['edges'] = edges
need_net['satisfiers'] = satisfiers
need_net['needs'] = needs


y = json.dumps(need_net, sort_keys=False, indent=4)
with open(selected_schema + '_need_net_survey.json', "w") as text_file:
    text_file.write(y)
                
    
loaded_net = {}
with open(selected_schema + '_need_net_survey.json', "r") as f:
    loaded_net = json.load(f)


### BEGIN PARSING FROM SURVEY RESULTS INTO THE CY GRAPH JSON

# Parameters to network styling
red_col = 'rgb(194, 109, 104)'
green_col = 'rgb(157, 170, 189)'
real_green = "rgb(128, 184, 122)"
node_col = 'rgb(41, 52, 64)'
large_col = 'rgb(65, 82, 101)'
text_col = 'rgb(200, 200, 200)'
label_col = 'rgb(44, 41, 51)'
neutral_grey = "rgb(150, 150, 150)"

large_opacity = '0.2'
node_opacity = '1'

big_link_width = 6
medium_link_width = 4
small_link_width = 2

node_size = 45

left_node_x = 100
right_node_x = left_node_x + 110




def affect_to_color(affect):
    if is_number_like(affect):
        affect = int(affect)
    
    
    to_ret = neutral_grey
    
    if affect == 1:
        # red, bad
        to_ret = red_col
    elif affect == 3:
        # good, blue
        to_ret = green_col
    else:
        to_ret = neutral_grey
        
    return to_ret
        
# TODO, make this scale somehow, rather then using bins
def satisfaction_to_width(satisfaction):
    if is_number_like(satisfaction):
        satisfaction = int(satisfaction)
    else:    
        satisfaction = -1
    
    if satisfaction < 30 and satisfaction > 0:
        # bad, small
        to_ret = small_link_width
    elif satisfaction > 79:
        # good, blue
        to_ret = big_link_width
    else:
        to_ret = medium_link_width
        
    return to_ret

def create_need(need, x, y):
    node_plus = \
    {
        "data": {
          "id": need['name'],
          "parent": need['category'],
          "label": need['name'],
          "fontsize": 8,
          "color": "rgb(41, 52, 64)",
          "opacity": "1",
          "textcolor": "rgb(200, 200, 200)"
        },
        "position": {
          "x": x,
          "y": y
        },
        "group": "nodes",
        "removed": False,
        "selected": False,
        "selectable": True,
        "locked": False,
        "grabbable": True,
        "pannable": False,
        "classes": "multiline-manual"
      }
        
    return node_plus


def create_parent_need(parent_name):
    node_plus = \
    {
        "data": {
          "id": parent_name,
          "label": parent_name,
          "fontsize": 15,
          "color": 'rgb(65, 82, 101)',
          "opacity": "0.2",
          "textcolor": "rgb(30, 30, 30)"
        },
        "group": "nodes",
        "removed": False,
        "selected": False,
        "selectable": True,
        "locked": False,
        "grabbable": True,
        "pannable": False
      }
        
    return node_plus

def create_needs(need_list):
    x_pos = 100
    y_0 = 60
    delta_y = 50
    
    new_need_list = []
    
    curr_y = y_0
    
    parents = set()
    
    for need in need_list:
        # if new group, increase the delta_y by a bit to give some space
        if need['category'] not in parents and len(parents) != 0:
            curr_y += 40
        parents.add(need['category'])
        new_need = create_need(need, x_pos, curr_y)
        new_need_list.append(new_need)
        
        
        curr_y = curr_y  + delta_y
        
    
    # we also need to collapse the parents into a unique list
    # and then create the parent nodes
    for parent in parents:
        new_need = create_parent_need(parent)
        new_need_list.append(new_need)
    
    return new_need_list


def create_satisfier(satisfier, x, y):
    node_plus = \
    {
        "data": {
          "id": satisfier['satisfier_label'],
          "label": satisfier['satisfier_label'],
          "fontsize": 8,
          "color": "rgb(41, 52, 64)",
          "opacity": "1",
          "textcolor": "rgb(200, 200, 200)"
        },
        "position": {
          "x": x,
          "y": y
        },
        "group": "nodes",
        "removed": False,
        "selected": False,
        "selectable": True,
        "locked": False,
        "grabbable": True,
        "pannable": False,
        "classes": "multiline-manual"
      }
        
    return node_plus


def create_satisfiers(satisfier_list):
    x_pos = 210
    y_0 = 50
    delta_y = 50
    
    new_satisfier_list = []
    
    curr_y = y_0
    
    for satisfier in satisfier_list:
        new_satisfier = create_satisfier(satisfier, x_pos, curr_y)
        new_satisfier_list.append(new_satisfier)
        curr_y = curr_y  + delta_y
    
    return new_satisfier_list

def create_edge(edge):
    edge_plus = \
    {
        "data": {
          "id": edge['need_id'] + "_" + edge['satisfier_id'],
          "source": edge['need_id'],
          "target": edge['satisfier_id'],
          "color": affect_to_color(edge['affect']), 
          "width": satisfaction_to_width(edge['satisfaction_contrib']),  # TODO - base this on how much it is satisfied
          "style": "solid"
        },
        "position": {
          "x": 0,
          "y": 0
        },
        "group": "edges",
        "removed": False,
        "selected": False,
        "selectable": True,
        "locked": False,
        "grabbable": True,
        "pannable": True,
        "classes": ""
      }
    return edge_plus


def create_edges(edge_list):
    new_edge_list = []

    for edge in edge_list:
        new_edge = create_edge(edge)
        new_edge_list.append(new_edge)
    
    return new_edge_list



def create_cyto(edges, needs, satisfiers, path_to_base, output_path):
    # open the base cyto and attach the elements to the object, then save
    base = {}
    with open(path_to_base, "r") as f:
        base = json.load(f)
        
    elements = {}
    
    elements['nodes'] = create_needs(needs) + create_satisfiers(satisfiers)
    elements['edges'] = create_edges(edges)
    
    base['elements'] = elements
    y = json.dumps(base, sort_keys=False, indent=4)
    with open(selected_schema + output_path, "w") as text_file:
        text_file.write(y)
    


create_cyto(loaded_net['edges'], loaded_net['needs'], loaded_net['satisfiers'], 'base_cyto.json', '_python_net_v7.json' )

print ("stop here to inspect objects")






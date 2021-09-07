#!/usr/bin/python

import json
import os
import html2text

filename = "./lab_data_mart_data.json"
json_object = json.load(open(filename))

nodes_list = json_object["x"]["nodes"]["tableName"]
edges_to_list = json_object["x"]["edges"]["to"]
edges_from_list = json_object["x"]["edges"]["from"]
edge_id_list = json_object["x"]["edges"]["id"]

#nodes = []
#edges = []
output_json = {}


#open soil data model json
f = open('./soil_data_model.json')
graph = json.load(f)

nodes = graph["nodes"]
edges = graph["edges"]

max_id=0
for node in nodes:
    if max_id < node["id"]:
        max_id=node["id"]

next_available_node_id = max_id+1


#add nodes
for node_name in nodes_list:
    node_index = nodes_list.index(node_name)
    label = json_object["x"]["nodes"]["label"][node_index]
    title = json_object["x"]["nodes"]["title"][node_index]
    node = {"id":next_available_node_id, "label":node_name, "title":html2text.html2text(title), "group":"Class"}
    next_available_node_id+=1
    nodes.append(node)


#add edges
def find_node_id(node_label):
    for node in nodes:    
        if node["label"]==node_label:
            return node["id"]

#add edges
for index in range(len(edges_from_list)):    
    from_node = edges_from_list[index]
    from_node_id = find_node_id(from_node)
    to_node = edges_to_list[index]
    to_node_id = find_node_id(to_node)
    edge_name = edge_id_list[index]
    edge_label = edge_name.split(':')[1].split('->')[1]
    edge = {"from":from_node_id, "to":to_node_id, "label":edge_label}
    edges.append(edge)

#add manual edge mappings
mappings_f = open('./manual_edge_mappings.json')
edge_mappings = json.load(mappings_f)
#print(edge_mappings)
#node specific info
n_info_f = open('./node_specific_info.json')
node_specific_info = json.load(n_info_f)
#print(node_specific_info)

#keeping a full set of nodes for lookup(since merge will delete some nodes)
nodes_copy = nodes


#find node id from label
def find_node_id(node_label):
    for node in nodes:
        if node["label"]==node_label:
            return node["id"]
    return -1
'''
for from_node,to_node in edge_mappings.items():
    from_node_id = find_node_id(from_node)
    to_node_id = find_node_id(to_node)
    if((from_node_id != -1) and (to_node_id != -1)):
        new_edge = {"from":from_node_id, "to":to_node_id, "label":"stored_as"}
        edges.append(new_edge)
    else:
        print("Error, node label not found: ")
        print("from: ", from_node, "to: ", to_node)
'''

def get_edges_for_node(node_id):
    connected_edges = []
    for edge in edges:
        if((edge["from"] == node_id) or (edge["to"] == node_id)):
            connected_edges.append(edge)
            #remove edge from edges
            edges.remove(edge)
    return connected_edges
            
def erase_node(node_id):
    for node in nodes:
        if node["id"]==node_id:
            nodes.remove(node)

def find_node_specific_info(node_label):
    for nl, node_info in node_specific_info.items():
        if nl == node_label:
            return node_info
    return -1

#erase node from nodes and return
def get_node(node_label):
    for node in nodes_copy:
        if node["label"]==node_label:
            return node
    #print("no node found for: ", node_label)
    return -1


#add node specific info for all nodes
for node in nodes:
    specific_info  = find_node_specific_info(node["label"])
    if specific_info != -1:
        for key, value in specific_info.items():
            #print(key,value)
            node[key]=value

def merge_nodes(from_node, to_node):
        from_node_id = from_node["id"]
        to_node_id = to_node["id"]
        edges_for_from_node = get_edges_for_node(from_node_id)
        edges_for_to_node = get_edges_for_node(to_node_id)
        all_edges = edges_for_from_node + edges_for_to_node
        #concat their node_specific info
        if "url" in to_node:
            if "url" in from_node:
                from_node["url"] = from_node["url"]+',\n\n'+to_node["url"]
            else:
                from_node["url"] = to_node["url"]
        if "description" in to_node:
            if "description" in from_node:
                from_node["description"] = from_node["description"]+'\n\n'+to_node["description"]
            else:
                from_node["description"] = to_node["description"]
        #node_specific_info = find_node_specific_info(to_node["label"])
        #if node_specific_info != -1:
        #    for key,value in node_specific_info.items():
        #        if key in from_node:
        #            from_node[key] += value
        #        else:
        #            from_node[key] = value
        #print(from_node)
        #erase to node
        erase_node(to_node["id"])
        #erase from node
        #erase_node(from_node["id"])
        #add new from node
        #nodes.append(from_node)
        #re-wire edges to node
        for edge in all_edges:
            if(edge["from"]==to_node["id"]):
                edge["from"]=from_node["id"]
            elif(edge["to"]==to_node["id"]):
                edge["to"]=from_node["id"]
            #add edge to edges
            edges.append(edge)
    


def merge_nodes_in_edge_mappings():
    for from_node_label, to_node_list in edge_mappings.items():
        #print("merging:", from_node_label, to_node_label)
        from_node = get_node(from_node_label)
        for to_node_label in to_node_list:
            to_node = get_node(to_node_label)
            if((from_node==-1) or (to_node==-1)):
                #print("not_found", from_node_label, to_node_label, from_node, to_node)
                continue
            else:
                merge_nodes(from_node, to_node)
        

merge_nodes_in_edge_mappings()                
        




#ouput network json
output_json["nodes"]=nodes
output_json["edges"]=edges
print(json.dumps(output_json))
#node_specific_info = {}
#output node specific info json
#for node in nodes:
#    node_name = node["label"]
#    print(html2text.html2text(node["title"]))
    
    


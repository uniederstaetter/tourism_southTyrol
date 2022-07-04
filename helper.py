import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def initialiseState():
    st.session_state['filtering'] = False
    st.session_state['standard'] = False
    st.session_state['duration'] = 'one-day'
    st.session_state['age'] = []
    st.session_state['accommodation'] = []
    st.session_state['tags'] = []
    st.session_state['seasons'] = []


def makeCombinationDf(combinations):
    combinationList = []
    for combination in combinations:
        source = combination[0]
        dest = combination[1]
        if source != dest:
            element = [source, dest, 0]
            combinationList.extend([element])

    return pd.DataFrame(combinationList, columns=['source_attraction', 'dest_attraction', 'counter'])


def findLatLonCoords(row, listToAdd, pois):
    """
    :return: Void. Adds for each source and dest POI their lat and long coordinates to a passed list.
    """
    source = row['source_attraction']
    dest = row['dest_attraction']
    counter = row['counter']

    lat_source = pois.loc[(pois['name'] == source), 'lat'].item()
    lon_source = pois.loc[(pois['name'] == source), 'long'].item()

    lat_dest = pois.loc[(pois['name'] == dest), 'lat'].item()
    lon_dest = pois.loc[(pois['name'] == dest), 'long'].item()

    listToAdd.append([source, lat_source, lon_source, dest, lat_dest, lon_dest, counter])


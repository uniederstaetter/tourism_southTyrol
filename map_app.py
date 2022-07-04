import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time
import constant

import functions
import functions as f
import filtering as filter
import helper as help

st.set_page_config(layout="wide")  # , initial_sidebar_state="expanded")

pois_withOutTransitions_oneDay = pd.read_csv('data/pois_outTransFreqOneDay.csv')
pois_withOutTransitions_fullVisit = pd.read_csv('data/pois_outTransFreqFullVisit.csv')

transitions_oneDay = pd.read_csv('data/subsetTransitions_one_day.csv')
transitions_fullVisit = pd.read_csv('data/subsetTransitions_full_visit.csv')

trajectories_oneDay = pd.read_csv('data/trajectories_types_one_day.csv')
trajectories_fullVist = pd.read_csv('data/trajectories_types_full_visit.csv')

pois_withCoordinates = pd.read_csv('data/accessPoints_lat_lon.csv')

# reads in the token used to visualise the mapbox map
mapbox_access_token = open(
    "token.mapbox_token").read()

# initalises all the state variables
help.initialiseState()

with st.sidebar:
    filtering = st.checkbox('Filter', False)
    if filtering:
        st.session_state.duration = st.radio("trajectory-duation",
                                             ('one day trajectories', 'full-visit trajectories'))
        st.session_state.age = st.multiselect(
            'Age Categories', constant.AGE)
        st.session_state.accommodation = st.multiselect(
            'Accommodation Type', constant.ACCOMMODATIONS)
        st.session_state.tags = st.multiselect(
            'Activity Categories', constant.TAGS)
        st.session_state.seasons = st.multiselect(
            'Seasons', constant.SEASONS)
        selectionButton = st.button('Filter', on_click=functions.filterMap)
        resetButton = st.button('Standard view')

# visualise standard map
mainFig = f.addMainFigure(mapbox_access_token)

if not filtering:
    st.plotly_chart(mainFig)
else:
    if selectionButton:
        duration = st.session_state.duration
        age = st.session_state.age
        ageSelection = age if len(age) > 0 else constant.AGE
        accommodation = st.session_state.accommodation
        accommodationSelection = accommodation if len(accommodation) > 0 else constant.ACCOMMODATIONS
        tags = st.session_state.tags
        tagsSelection = tags if len(tags) > 0 else constant.TAGS
        season = st.session_state.seasons
        seasonSelection = season if len(season) > 0 else constant.SEASONS

        # TODO: check if all selections are empty - no filtering needed.
        if len(age) < 0 and len(accommodation) < 0 and len(tags) < 0 and len(season) < 0:  # all selections are empty
            noFilterMessage = st.info('No filtering was selected.')
            for seconds in range(4):
                time.sleep(1)
            noFilterMessage.empty()
        else:
            nonZeroFilteredTransition, filteredAttractionFrequencies = filter.filterData(ageSelection,
                                                                                         accommodationSelection,
                                                                                         duration, tagsSelection,
                                                                                         seasonSelection)
            if nonZeroFilteredTransition is None:
                noDataFoundMessage = st.info(
                    'No data was found for your selection. Please change your selection. Displaying now standard view')
                for seconds in range(4):
                    time.sleep(1)
                noDataFoundMessage.empty()
                st.plotly_chart(mainFig)
            else:
                updatedFig = f.updateFigure(mainFig, filteredAttractionFrequencies, nonZeroFilteredTransition)
                st.plotly_chart(updatedFig)

    elif resetButton or not selectionButton:
        st.plotly_chart(mainFig)

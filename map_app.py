import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time
import constant

import functions
import functions as f
import filtering as filter
import helper as help

st.set_page_config(layout="wide",  page_title="TouristInSouthTyrol",  page_icon="img/logo.png")  # , initial_sidebar_state="expanded")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Ranchers&family=Roboto:wght@400;700&display=swap');

html, body, [class*="css"]  {
font-family: 'Roboto', sans-serif;
}
.title{
    font-family: 'Ranchers', cursive;
    color:#b31939;
    font-size: 32px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 10%;
}
div.stButton > button:first-child {
    font-family: 'Ranchers', cursive;
    font-size: 15px;
    background-color:#b31939;
    font-weight:bold;
    border-color: #b31939;
}
div.stButton > button:hover {
    color: #000000
}
.row-widget {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


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
    title_styled = '<p class = "title">TouristSouthTyrol</p>'
    st.markdown(title_styled, unsafe_allow_html=True)
    st.session_state.duration = st.radio("Trajectory Duration", ('one-day', 'full-visit'))
    filtering = st.checkbox('Filter', False)
    if filtering:
        st.session_state.age = st.multiselect(
            'Age Categories', constant.AGE)
        st.session_state.accommodation = st.multiselect(
            'Accommodation Type', constant.ACCOMMODATIONS)
        st.session_state.tags = st.multiselect(
            'Activity Categories', constant.TAGS)
        st.session_state.seasons = st.multiselect(
            'Seasons', constant.SEASONS)
        selectionButton = st.button('Filter')
        resetButton = st.button('Standard view', on_click=help.clearState)

# building both standard maps
mainFig_oneDay, mainFig_fullVisit = f.addMainFigure(mapbox_access_token)


if not filtering:
    if st.session_state.duration == 'one-day':
        st.plotly_chart(mainFig_oneDay)
    else:
        st.plotly_chart(mainFig_fullVisit)
else:
    if selectionButton:
        age = st.session_state.age
        ageSelection = age if len(age) > 0 else constant.AGE
        accommodation = st.session_state.accommodation
        accommodationSelection = accommodation if len(accommodation) > 0 else constant.ACCOMMODATIONS
        tags = st.session_state.tags
        tagsSelection = tags if len(tags) > 0 else constant.TAGS
        season = st.session_state.seasons
        seasonSelection = season if len(season) > 0 else constant.SEASONS
        if len(age) == 0 and len(accommodation) == 0 and len(tags) == 0 and len(season) == 0:
            noFilterMessage = st.info('No filtering was selected.')
            if st.session_state.duration == 'one-day':
                st.plotly_chart(mainFig_oneDay)
            else:
                st.plotly_chart(mainFig_fullVisit)
            for seconds in range(4):
                time.sleep(1)
            noFilterMessage.empty()

        else:
            nonZeroFilteredTransition, filteredAttractionFrequencies = filter.filterData(ageSelection,
                                                                                         accommodationSelection,
                                                                                         tagsSelection,
                                                                                         seasonSelection)
            if nonZeroFilteredTransition is None:
                noDataFoundMessage = st.info(
                    'No data was found for your selection. Please change your selection. Displaying now standard view')
                if st.session_state.duration == 'one-day':
                    st.plotly_chart(mainFig_oneDay)
                else:
                    st.plotly_chart(mainFig_fullVisit)
                for seconds in range(4):
                    time.sleep(1)
                noDataFoundMessage.empty()
            else:

                updatedFig = f.updateFigure(mainFig_oneDay, filteredAttractionFrequencies,nonZeroFilteredTransition) if st.session_state.duration == 'one-day' else f.updateFigure(mainFig_fullVisit, filteredAttractionFrequencies,nonZeroFilteredTransition)

                st.plotly_chart(updatedFig)
    else:  # not filterButton
        if st.session_state.duration == 'one-day':
            st.plotly_chart(mainFig_oneDay)
        else:
            st.plotly_chart(mainFig_fullVisit)

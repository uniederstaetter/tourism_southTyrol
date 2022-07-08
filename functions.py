import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import helper as help
import ast

pois_withOutTransitions_oneDay = pd.read_csv('data/pois_outTransFreqOneDay.csv')
pois_withOutTransitions_fullVisit = pd.read_csv('data/pois_outTransFreqFullVisit.csv')
transitions_oneDay = pd.read_csv('data/subsetTransitions_one_day.csv')
transitions_fullVisit = pd.read_csv('data/subsetTransitions_full_visit.csv')


def drawPointsAndLines(figure, transitionData, poiData):
    maxOutTransitionFreq = poiData['outTransFrequency'].max()
    minOutTransitionFreq = poiData['outTransFrequency'].min()
    highestRank = int(pois_withOutTransitions_oneDay['rank'].max()) if st.session_state.duration == 'one-day' else int(pois_withOutTransitions_fullVisit['rank'].max())
    poiInspectorList = poiData[['name', 'type', 'tags', 'rank', 'mostSimilar']].values.tolist()
    poiInspector = ['<b>' + poiName + '</b><br><br>' \
                    '<b>Category: </b>' + poiType + '<br>' \
                    '<b>Tags: </b>' + ' -- '.join([t for t in ast.literal_eval(poiTags)]) + '<br>' \
                     '<b>Rank: </b>' + str(int(poiRank)) + '/' + str(highestRank) + '<br>' \
                     '<b>Alternatives: </b>' + ' -- '.join([t for t in ast.literal_eval(poiAlternatives)]) + '<br>' if int(poiRank) > 10 else
                    '<b>' + poiName + '</b><br><br>' \
                     '<b>Category: </b>' + poiType + '<br>' \
                      '<b>Tags: </b>' + ' -- '.join([t for t in ast.literal_eval(poiTags)]) + '<br>' \
                      '<b>Rank: </b>' + str(int(poiRank)) + '<b> !!HOTSPOT ALARM!!</b><br>' \
                      '<b>Alternatives: </b>' + ' -- '.join([t for t in ast.literal_eval(poiAlternatives)]) + '<br>' for
                    poiName, poiType, poiTags, poiRank, poiAlternatives in poiInspectorList]

    figure.add_trace(
        go.Scattermapbox(
            mode="lines",
            lon=list(transitionData['src_lon'].values) + list(transitionData['dest_lon'].values),
            lat=list(transitionData['src_lat'].values) + list(transitionData['dest_lat'].values),
            # text=list(str(transitionData['counter'].values)),
            line=dict(color='black', width=.4),
            opacity=.8
        )
    )
    figure.add_trace(go.Scattermapbox(
        lat=poiData['lat'],
        lon=poiData['long'],
        hoverinfo='text',
        text=poiInspector,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=12,
            color=poiData['outTransFrequency'],
            cmin=minOutTransitionFreq,
            cmax=maxOutTransitionFreq,
            colorscale=[[0, "rgb(178,24,43)"], [0.01, "rgb(244,165,130)"], [0.02, "rgb(247,247,247)"],
                        [0.05, "rgb(209,229,240)"], [0.09, "rgb(146,197,222)"],
                        [0.5, "rgb(33,102,172)"], [1, "rgb(5,48,97)"]]
        )
    ))
    return figure


def addMainFigure(token):
    fig = go.Figure()
    fig.update_layout(
        showlegend=False,
        autosize=False,
        width=1600,
        height=900,
        margin=dict(l=0, r=0, t=-0, b=0),
        hovermode='closest',
        mapbox=dict(
            accesstoken=token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=46.6,
                lon=11.4
            ),
            pitch=0,
            zoom=7.8,
            style='open-street-map'
        )
    )

    mainFigure_oneDay = drawPointsAndLines(fig, transitions_oneDay, pois_withOutTransitions_oneDay)
    mainFigure_fullVisit = drawPointsAndLines(fig, transitions_fullVisit, pois_withOutTransitions_fullVisit)

    return mainFigure_oneDay, mainFigure_fullVisit


def updateFigure(fig, filteredPois, filteredTransitions):
    updatedFig = fig.update_traces(
        patch=dict(lat=[],
                   lon=[],
                   mode='none',
                   line={},
                   marker={},
                   text=[]),
        overwrite=True)
    return drawPointsAndLines(updatedFig, filteredTransitions, filteredPois)


def filterMap():
    st.session_state.filtering = True


def resetMap(fig):
    st.session_state.standard = True
    updatedFigure = fig.update_traces(
        patch=dict(lat=[],
                   lon=[],
                   mode='none',
                   line={},
                   marker={},
                   text=[]),
        overwrite=True)
    return updatedFigure

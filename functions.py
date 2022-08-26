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
    # calculate rank
    poiData['calculatedRank'] = poiData['outTransFrequency'].rank(method='max', ascending=False)
    highestRank_dataset = int(poiData['calculatedRank'].max())

    poiInspectorList = poiData[['name', 'type', 'tags', 'calculatedRank', 'mostSimilar', 'top3InTransitions',
                                'top3OutTransitions']].values.tolist()
    poiInspector = ['<b>' + poiName + '</b><br><br>' \
                                      '<b>Category: </b>' + poiType + '<br>' \
                                                                      '<b>Tags: </b>' + ' -- '.join(
        [t for t in ast.literal_eval(poiTags)]) + '<br><br>' \
                                                  '<b>Rank: </b>' + str(int(poiRank)) + '/' + str(
        highestRank_dataset) + '<br>' \
                               '<b>Mostly coming from: </b>' \
                    + '-- '.join([inTransPois for inTransPois in ast.literal_eval(poiInTrans)]) + '<br>' \
                                                                                                  '<b>Mostly going to: </b>' \
                    + '-- '.join([outTransPois for outTransPois in ast.literal_eval(poiOutTrans)]) + '<br>' \
                                                                                                     '<b>Alternatives: </b>' + ' -- '.join(
        [t for t in ast.literal_eval(poiAlternatives)]) + '<br>' if int(poiRank) > 10 else
                    '<b>' + poiName + '</b><br><br>' \
                                      '<b>Category: </b>' + poiType + '<br>' \
                                                                      '<b>Tags: </b>' + ' -- '.join(
                        [t for t in ast.literal_eval(poiTags)]) + '<br><br>' \
                                                                  '<b>Mostly coming from: </b>' \
                    + '-- '.join([inTransPois for inTransPois in ast.literal_eval(poiInTrans)]) + '<br>' \
                                                                                                  '<b>Mostly going to: </b>' \
                    + '-- '.join([outTransPois for outTransPois in ast.literal_eval(poiOutTrans)]) + '<br>' \
                                                                                                     '<b>Rank: </b>' + str(
                        int(poiRank)) + '<b> !!HOTSPOT ALARM!!</b><br>' \
                                        '<b>Alternatives: </b>' + ' -- '.join(
                        [t for t in ast.literal_eval(poiAlternatives)]) + '<br>' for
                    poiName, poiType, poiTags, poiRank, poiAlternatives, poiInTrans, poiOutTrans in poiInspectorList]

    figure.add_trace(
        go.Scattermapbox(
            mode="lines",
            lon=list(transitionData['src_lon'].values) + list(transitionData['dest_lon'].values),
            lat=list(transitionData['src_lat'].values) + list(transitionData['dest_lat'].values),
            # text=list(str(transitionData['counter'].values)),
            line=dict(color='black', width=.4),
            opacity=.8,
            showlegend=False
        )
    )
    figure.add_trace(go.Scattermapbox(
        showlegend=False,
        lat=poiData['lat'],
        lon=poiData['long'],
        hoverinfo='text',
        text=poiInspector,
        mode='markers',
        marker=go.scattermapbox.Marker(
            showscale=True,
            size=12,
            color=poiData['outTransFrequency'],
            cmin=minOutTransitionFreq,
            cmax=maxOutTransitionFreq,
            colorscale=[[0.0, 'rgb(240, 142, 98)'], [0.001, 'rgb(231, 109, 84)'],
                        [0.009, 'rgb(216, 80, 83)'], [0.02, 'rgb(195, 56, 90)'],
                        [0.05, 'rgb(168, 40, 96)'], [0.09, 'rgb(138, 29, 99)'],
                        [0.5, 'rgb(107, 24, 93)'], [1.0, 'rgb(47, 15, 61)']],
            colorbar=dict(
                title='Visit Frequency'
            )
        )
    ))
    return figure


def drawPoints(figure, poiData):
    maxOutTransitionFreq = poiData['outTransFrequency'].max()
    minOutTransitionFreq = poiData['outTransFrequency'].min()
    # calculate rank
    poiData['calculatedRank'] = poiData['outTransFrequency'].rank(method='max', ascending=False)
    highestRank_dataset = int(poiData['calculatedRank'].max())

    poiInspectorList = poiData[['name', 'type', 'tags', 'calculatedRank', 'mostSimilar', 'top3InTransitions',
                                'top3OutTransitions']].values.tolist()
    print(poiInspectorList)
    poiInspector = ['<b>' + poiName + '</b><br><br>' \
                                      '<b>Category: </b>' + poiType + '<br>' \
                                                                      '<b>Tags: </b>' + ' -- '.join(
        [t for t in ast.literal_eval(poiTags)]) + '<br><br>' \
                                                  '<b>Rank: </b>' + str(int(poiRank)) + '/' + str(
        highestRank_dataset) + '<br>' \
                               '<b>Mostly coming from: </b>' \
                    + '-- '.join([inTransPois for inTransPois in ast.literal_eval(poiInTrans)]) + '<br>' \
                                                                                                  '<b>Mostly going to: </b>' \
                    + '-- '.join([outTransPois for outTransPois in ast.literal_eval(poiOutTrans)]) + '<br>' \
                                                                                                     '<b>Alternatives: </b>' + ' -- '.join(
        [t for t in ast.literal_eval(poiAlternatives)]) + '<br>' if int(poiRank) > 10 else
                    '<b>' + poiName + '</b><br><br>' \
                                      '<b>Category: </b>' + poiType + '<br>' \
                                                                      '<b>Tags: </b>' + ' -- '.join(
                        [t for t in ast.literal_eval(poiTags)]) + '<br><br>' \
                                                                  '<b>Mostly coming from: </b>' \
                    + '-- '.join([inTransPois for inTransPois in ast.literal_eval(poiInTrans)]) + '<br>' \
                                                                                                  '<b>Mostly going to: </b>' \
                    + '-- '.join([outTransPois for outTransPois in ast.literal_eval(poiOutTrans)]) + '<br>' \
                                                                                                     '<b>Rank: </b>' + str(
                        int(poiRank)) + '<b> !!HOTSPOT ALARM!!</b><br>' \
                                        '<b>Alternatives: </b>' + ' -- '.join(
                        [t for t in ast.literal_eval(poiAlternatives)]) + '<br>' for
                    poiName, poiType, poiTags, poiRank, poiAlternatives, poiInTrans, poiOutTrans in poiInspectorList]

    figure.add_trace(go.Scattermapbox(
        showlegend=False,
        lat=poiData['lat'],
        lon=poiData['long'],
        hoverinfo='text',
        text=poiInspector,
        mode='markers',
        marker=go.scattermapbox.Marker(
            showscale=True,
            size=12,
            color=poiData['outTransFrequency'],
            cmin=minOutTransitionFreq,
            cmax=maxOutTransitionFreq,
            colorscale=[[0.0, 'rgb(240, 142, 98)'], [0.001, 'rgb(231, 109, 84)'],
                        [0.009, 'rgb(216, 80, 83)'], [0.02, 'rgb(195, 56, 90)'],
                        [0.05, 'rgb(168, 40, 96)'], [0.09, 'rgb(138, 29, 99)'],
                        [0.5, 'rgb(107, 24, 93)'], [1.0, 'rgb(47, 15, 61)']],
            colorbar=dict(
                title='Visit Frequency'
            )
        )
    ))
    return figure


def addMainFigure(token):
    fig = go.Figure()
    fig.update_layout(
        autosize=False,
        width=2000,
        height=450,
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


def updateFigureOnlyPOIs(fig, filteredPois):
    updatedFig = fig.update_traces(
        patch=dict(lat=[],
                   lon=[],
                   mode='none',
                   line={},
                   marker={},
                   text=[]),
        overwrite=True)
    return drawPoints(updatedFig, filteredPois)


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

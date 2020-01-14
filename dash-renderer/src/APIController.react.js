import {connect} from 'react-redux';
import {includes, isEmpty, isNil} from 'ramda';
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import TreeContainer, {getLoadingState} from './TreeContainer';
import GlobalErrorContainer from './components/error/GlobalErrorContainer.react';
import {
    computeGraphs,
    computePaths,
    hydrateInitialOutputs,
    setLayout,
} from './actions/index';
import {applyPersistence} from './persistence';
import apiThunk from './actions/api';
import {getAppState} from './reducers/constants';
import {STATUS} from './constants/constants';

/**
 * Fire off API calls for initialization
 */
class UnconnectedContainer extends Component {
    constructor(props) {
        super(props);
        this.initialization = this.initialization.bind(this);
        this.state = {
            errorLoading: false,
        };
    }
    componentDidMount() {
        this.initialization(this.props);
    }

    componentWillReceiveProps(props) {
        this.initialization(props);
    }

    initialization(props) {
        const {
            appLifecycle,
            dependenciesRequest,
            dispatch,
            graphs,
            layout,
            layoutRequest,
            paths,
        } = props;

        if (isEmpty(layoutRequest)) {
            dispatch(apiThunk('_dash-layout', 'GET', 'layoutRequest'));
        } else if (layoutRequest.status === STATUS.OK) {
            if (isEmpty(layout)) {
                const finalLayout = applyPersistence(
                    layoutRequest.content,
                    dispatch
                );
                dispatch(setLayout(finalLayout));
            } else if (isNil(paths)) {
                dispatch(computePaths({subTree: layout, startingPath: []}));
            }
        }

        if (isEmpty(dependenciesRequest)) {
            dispatch(
                apiThunk('_dash-dependencies', 'GET', 'dependenciesRequest')
            );
        } else if (
            dependenciesRequest.status === STATUS.OK &&
            isEmpty(graphs)
        ) {
            dispatch(computeGraphs(dependenciesRequest.content));
        }

        if (
            // dependenciesRequest and its computed stores
            dependenciesRequest.status === STATUS.OK &&
            !isEmpty(graphs) &&
            // LayoutRequest and its computed stores
            layoutRequest.status === STATUS.OK &&
            !isEmpty(layout) &&
            !isNil(paths) &&
            // Hasn't already hydrated
            appLifecycle === getAppState('STARTED')
        ) {
            let errorLoading = false;
            try {
                dispatch(hydrateInitialOutputs());
            } catch (err) {
                errorLoading = true;
            } finally {
                this.setState(state =>
                    state.errorLoading !== errorLoading ? {errorLoading} : null
                );
            }
        }
    }

    render() {
        const {
            appLifecycle,
            dependenciesRequest,
            dispatch,
            layoutRequest,
            layout,
            requestQueue,
            config,
        } = this.props;

        const {errorLoading} = this.state;

        if (
            layoutRequest.status &&
            !includes(layoutRequest.status, [STATUS.OK, 'loading'])
        ) {
            return <div className="_dash-error">Error loading layout</div>;
        } else if (
            errorLoading ||
            (dependenciesRequest.status &&
                !includes(dependenciesRequest.status, [STATUS.OK, 'loading']))
        ) {
            return (
                <div className="_dash-error">Error loading dependencies</div>
            );
        } else if (appLifecycle === getAppState('HYDRATED')) {
            const container = (
                <TreeContainer
                    _dashprivate_layout={layout}
                    _dashprivate_path={[]}
                    _dashprivate_dependencies={dependenciesRequest.content}
                    _dashprivate_dispatch={dispatch}
                    _dashprivate_loadingState={getLoadingState(
                        layout,
                        requestQueue
                    )}
                    _dashprivate_requestQueue={requestQueue}
                    _dashprivate_config={config}
                />
            );

            return config.ui === true ? (
                <GlobalErrorContainer>{container}</GlobalErrorContainer>
            ) : (
                container
            );
        }

        return <div className="_dash-loading">Loading...</div>;
    }
}
UnconnectedContainer.propTypes = {
    appLifecycle: PropTypes.oneOf([
        getAppState('STARTED'),
        getAppState('HYDRATED'),
    ]),
    dispatch: PropTypes.func,
    dependenciesRequest: PropTypes.object,
    layoutRequest: PropTypes.object,
    layout: PropTypes.object,
    paths: PropTypes.object,
    history: PropTypes.any,
    error: PropTypes.object,
    config: PropTypes.object,
    requestQueue: PropTypes.array,
};

const Container = connect(
    // map state to props
    state => ({
        appLifecycle: state.appLifecycle,
        dependenciesRequest: state.dependenciesRequest,
        layoutRequest: state.layoutRequest,
        layout: state.layout,
        graphs: state.graphs,
        paths: state.paths,
        requestQueue: state.requestQueue,
        history: state.history,
        error: state.error,
        config: state.config,
    }),
    dispatch => ({dispatch})
)(UnconnectedContainer);

export default Container;

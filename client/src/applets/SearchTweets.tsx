import React, { useReducer, createContext } from 'react';
import InterestifyTable from '../components/FunctionalTable';
import { SearchState, searchReducer } from '../common/Reducers';
import ApiService from '../services/ApiService';
import { Grid, Typography, Box } from '@mui/material';
import Applet from '../components/Applet';
import SearchForm from '../components/SearchForm';

interface SearchTweetsProps {
    id?: string
    width?: string,
    height?: string,
}

const SearchTweets = (props: SearchTweetsProps): JSX.Element => {
    const apiService = new ApiService();

    const { id, width, height } = props;

    // set initial state
    const initialState: SearchState = {
        isLoading: false,
        query: '',
        tableData: {
            header: [
                { id: 'tweet', title: 'Tweet' },
                { id: 'retweetCount', title: 'Retweets' },
                { id: 'screenName', title: 'Screen\u00a0Name' },
                { id: 'location', title: 'Location' }
            ],
            body: []
        },
        error: '',
        searchKey: ''
    };

    const [state, dispatch] = useReducer(searchReducer, initialState);

    const StateContext = createContext(state); // context containing state

    // search logic
    const run = () => {
        if (state.query !== '') {
            apiService.searchTweets(state.query).then(res => {
                var body: any[] = [];
                res.data.forEach((obj: any) => {
                    body.push({
                        tweet: obj.text,
                        retweetCount: obj.retweet_count,
                        screenName: '@' + obj.user.screen_name,
                        location: obj.user.location
                    });
                });

                dispatch({ type: 'completeSearch', payload: { body } })
            }).catch(err => {
                console.log(err);
                dispatch({ type: 'error', payload: { error: err } });
            });
        }
    };

    return (
        <Applet title="Search Tweets" id={id} width={width} height={height} StateContext={StateContext} run={run}>
            <Grid container spacing={3}>
                <Grid item xs={12}>
                    <SearchForm searchKey={state.searchKey} dispatch={dispatch} />
                </Grid>
                <Grid item xs={12}>
                    {
                        state.tableData.body.length > 0 ? 
                        <InterestifyTable 
                            header={state.tableData.header} 
                            body={state.tableData.body} 
                            striped 
                            sortable 
                            missingValue="N/A"
                            pagination={{
                                rowsPerPageOptions: [5, 10, 15],
                                rowsPerPage: 5,
                            }}
                            sort={{
                                id: 'retweetCount',
                                order: 'desc'
                            }} 
                        /> :
                        <Box 
                            display="flex" 
                            justifyContent="center" 
                            alignItems="center" 
                            minHeight="200px"
                        >
                            <Typography variant="body2" color="text.secondary">
                                Enter a search term to find tweets
                            </Typography>
                        </Box>
                    }
                </Grid>
            </Grid>
        </Applet>
    );
}

export default SearchTweets;
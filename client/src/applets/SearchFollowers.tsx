import React, { useReducer, createContext } from 'react';
import { Grid, Typography, Box } from '@mui/material';
import InterestifyTable from '../components/FunctionalTable';
import ApiService from '../services/ApiService';
import Applet from '../components/Applet';
import { searchReducer, SearchState } from '../common/Reducers';
import SearchForm from '../components/SearchForm';

interface SearchFollowersProps {
    id?: string
    width?: string,
    height?: string,
}

const SearchFollowers = (props: SearchFollowersProps) => {
    const apiService = new ApiService();

    const { id, width, height } = props;

    // set initial state
    const initialState: SearchState = {
        isLoading: false,
        query: '',
        tableData: {
            header: [
                { id: 'screenName', title: 'Screen\u00a0Name' },
            ],
            body: []
        },
        error: '',
        searchKey: ''
    };

    const [state, dispatch] = useReducer(searchReducer, initialState);

    const StateContext = createContext(state); // context containing state

    // search logic
    const run = (): void => {
        if (state.query !== '') {
            apiService.getFollowers(state.query).then(res => {
                var body: any[] = [];
                res.data.forEach((obj: any) => {
                    body.push({
                        screenName: '@' + obj
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
        <Applet title="Search Followers" id={id} width={width} height={height} StateContext={StateContext} run={run}>
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
                                Enter a username to find followers
                            </Typography>
                        </Box>
                    }
                </Grid>
            </Grid>
        </Applet>
    );
}

export default SearchFollowers;
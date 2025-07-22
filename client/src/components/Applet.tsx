import React, { useState, useEffect, useContext, Context } from 'react';
import Panel from '../components/Panel';
import { CircularProgress, Grid, Typography, Box } from '@mui/material';

interface AppletProps {
    title: string
    id?: string
    width?: string,
    height?: string,
    children: React.ReactNode,
    StateContext: Context<any>,
    run: Function,
    Toolbar?: Function
}

const Applet = (props: AppletProps): JSX.Element => {
    const { title, id, width, height, StateContext, run, Toolbar } = props;
    const [overflow, setOverflow] = useState('hidden'); // set overflow initial state

    const state = useContext(StateContext); // context containing the state

    /**
     * updates overflow property
     * overflow is set to scroll when there is content available
     * and false otherwise
     */
    useEffect(() => {
        if (state.tableData.body.length > 0) {
            setOverflow('scroll');
        }
    }, [state.tableData.body]);

    // run applet logic
    useEffect(() => {
        run();
    }, [run]);

    return (
        <Panel id={id} width={width} height={height} overflow={overflow} title={title}>
            <Grid container spacing={2}>
                {
                    Toolbar && (
                        <Grid item xs={12}>
                            <Toolbar />
                        </Grid>
                    )
                }
                {
                    state.isLoading && (
                        <Grid item xs={12}>
                            <Box 
                                display="flex" 
                                justifyContent="center" 
                                alignItems="center"
                                sx={{ 
                                    height: '200px',
                                    flexDirection: 'column',
                                    gap: 2
                                }}
                            >
                                <CircularProgress 
                                    color="primary"
                                    size={40}
                                />
                                <Typography variant="body2" color="text.secondary">
                                    Loading...
                                </Typography>
                            </Box>
                        </Grid>
                    )
                }
                {
                    !state.isLoading && (
                        <Grid item xs={12}>
                            <Box sx={{ mt: 1 }}>
                                {props.children}
                            </Box>
                        </Grid>
                    )
                }
            </Grid>
        </Panel>
    );
}

export default Applet;
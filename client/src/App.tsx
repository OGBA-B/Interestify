import React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, Grid, IconButton, AppBar, Toolbar, Container } from '@mui/material';
import './App.css';
import SearchTweets from './applets/SearchTweets';
import SearchFollowers from './applets/SearchFollowers';
import Dashboard from './applets/Dashboard';
import materialTheme from './theme/materialTheme';

function App() {
  return (
    <ThemeProvider theme={materialTheme}>
      <CssBaseline />
      <div className="App">
        <AppBar position="static" elevation={0}>
          <Toolbar>
            <IconButton
              edge="start"
              color="inherit"
              onClick={() => {}}
              aria-label="Interestify"
              size="large"
              sx={{ mr: 2 }}
            >
              <img width="30px" src={require('./logo.svg')} alt="logo" />
            </IconButton>
          </Toolbar>
        </AppBar>
        
        <Container maxWidth="xl" sx={{ mt: 3 }}>
          <Grid container spacing={3}>
            {/* Dashboard takes full width on top */}
            <Grid xs={12} item>
              <Dashboard height="60vh" />
            </Grid>
            
            {/* Original applets below */}
            <Grid xs={12} sm={12} md={6} item>
              <SearchTweets height="50vh" />
            </Grid>
            <Grid xs={12} sm={12} md={6} item>
              <SearchFollowers height="50vh" />
            </Grid>
          </Grid>
        </Container>
      </div>
    </ThemeProvider>
  );
}

export default App;

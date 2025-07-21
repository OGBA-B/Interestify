import React from 'react';
import './App.css';
import SearchTweets from './applets/SearchTweets';
import SearchFollowers from './applets/SearchFollowers';
import Dashboard from './applets/Dashboard';
import { Grid, IconButton } from '@material-ui/core';

function App() {
  return (
    <div className="App">
      <nav className="navbar bg-dark">
        <ul className="navbar-nav">
          <li className="navbar-item">
          <IconButton
            className="navbar-brand"
            onClick={ () => {} }
            aria-label="Interestify"
            size="small">
              <img width="30px" src={ require('./logo.svg') } alt="logo" />
          </IconButton>
          </li>
        </ul>
      </nav>
      <br />
      <div className="container">
        <Grid container spacing={ 2 }>
          {/* Dashboard takes full width on top */}
          <Grid xs={ 12 } item>
            <Dashboard height="60vh" />
          </Grid>
          
          {/* Original applets below */}
          <Grid xs={ 12 } sm={ 12 } md={ 6 } item>
            <SearchTweets height="50vh" />
          </Grid>
          <Grid xs={ 12 } sm={ 12 } md={ 6 } item>
            <SearchFollowers height="50vh" />
          </Grid>
        </Grid>
      </div>
    </div>
  );
}

export default App;

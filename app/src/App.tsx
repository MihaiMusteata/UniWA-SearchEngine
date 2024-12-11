import * as React from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import Divider from '@mui/material/Divider';
import AppAppBar from './components/AppAppBar';
import Hero from './components/Hero';
import Footer from './components/Footer';
import AppTheme from './shared-theme/AppTheme';

export default function App(props: { disableCustomTheme?: boolean }) {
    return (
        <AppTheme {...props}>
            <CssBaseline enableColorScheme/>

            <AppAppBar/>
            <Hero/>
            <Divider/>
            <Footer/>
        </AppTheme>
    );
}

import * as React from 'react';
import {useState} from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import InputLabel from '@mui/material/InputLabel';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import Document from './Document';

import {visuallyHidden} from '@mui/utils';
import {Paper, Table, TableBody, TableCell, TableContainer, TableRow} from "@mui/material";

export default function Hero() {
    const [query, setQuery] = useState("");
    const [matchingDocs, setMatchingDocs] = useState([]);
    const [rankedTfIdf, setRankedTfIdf] = useState([]);
    const [rankedBm25, setRankedBm25] = useState([]);

    const handleSearch = async () => {
        const response = await fetch("http://127.0.0.1:5000/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
        });
        const data = await response.json();
        setMatchingDocs(data.matching_docs);
        setRankedTfIdf(data.ranked_tf_idf);
        setRankedBm25(data.ranked_bm25);
    };


    return (
        <Box
            id="hero"
            sx={(theme) => ({
                width: '100%',
                backgroundRepeat: 'no-repeat',

                backgroundImage:
                    'radial-gradient(ellipse 80% 50% at 50% -20%, hsl(210, 100%, 90%), transparent)',
                ...theme.applyStyles('dark', {
                    backgroundImage:
                        'radial-gradient(ellipse 80% 50% at 50% -20%, hsl(210, 100%, 16%), transparent)',
                }),
            })}
        >
            <Container
                sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    pt: 20,
                    pb: 5,
                }}
            >
                <Stack
                    spacing={2}
                    useFlexGap
                    sx={{alignItems: 'center', width: {xs: '100%', sm: '70%'}}}
                >
                    <Typography
                        variant="h1"
                        sx={{
                            display: 'flex',
                            flexDirection: {xs: 'column', sm: 'row'},
                            alignItems: 'center',
                            fontSize: 'clamp(3rem, 10vw, 3.5rem)',
                        }}
                    >
                        Tripadvisor&nbsp;
                        <Typography
                            component="span"
                            variant="h1"
                            sx={(theme) => ({
                                fontSize: 'inherit',
                                color: 'primary.main',
                                ...theme.applyStyles('dark', {
                                    color: 'primary.light',
                                }),
                            })}
                        >
                            Search Engine
                        </Typography>
                    </Typography>
                    <Typography
                        sx={{
                            textAlign: 'center',
                            color: 'text.secondary',
                            width: {sm: '100%', md: '80%'},
                        }}
                    >
                        Information Retrieval: Search Engine for hotels based on data collected from Tripadvisor.
                    </Typography>
                    <Stack
                        direction={{xs: 'column', sm: 'row'}}
                        spacing={1}
                        useFlexGap
                        sx={{pt: 2, width: '100%'}}
                    >
                        <InputLabel sx={visuallyHidden}>
                            Query
                        </InputLabel>
                        <TextField
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            id="query"
                            hiddenLabel
                            size="medium"
                            variant="outlined"
                            aria-label="Enter your query"
                            placeholder="Enter your query"
                            fullWidth
                            slotProps={{
                                htmlInput: {
                                    autoComplete: 'off',
                                    'aria-label': 'Enter your query',
                                },
                            }}
                        />
                        <Button
                            variant="contained"
                            color="primary"
                            size="small"
                            sx={{minWidth: 'fit-content'}}
                            onClick={handleSearch}
                        >
                            Search
                        </Button>
                    </Stack>
                    <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{textAlign: 'center'}}
                    >
                        You should enter a boolean query, using the following operators: AND, OR, NOT. For example: "Wifi AND Spa"
                    </Typography>
                </Stack>
                <Box
                    sx={{
                        display: 'flex',
                        flexDirection: 'row',
                        justifyContent: 'space-between',
                        gap: 4,
                        width: '100%',
                        marginTop: 8,
                    }}
                >
                    {/* Result Table */}
                    <Box
                        sx={{
                            flex: 1,
                            borderRadius: 1,
                            border: '1px solid',
                            borderColor: 'hsla(220, 25%, 80%, 0.2)',
                            outline: '1px solid',
                            outlineColor: 'hsla(220, 25%, 80%, 0.2)',
                            boxShadow: '0 0 12px 8px hsla(220, 25%, 80%, 0.2)',
                            padding: 2,
                            marginBottom: 4,
                        }}
                    >
                        <Typography variant="h6" align="center" sx={{ marginBottom: 2 }}>
                            Matching Documents
                        </Typography>
                        <TableContainer>
                            <Table>
                                <TableBody>
                                    {
                                        matchingDocs.map((doc, index) => (
                                            <TableRow key={index}>
                                                <TableCell align="center">
                                                    <Document {...doc} />
                                                </TableCell>
                                            </TableRow>
                                        ))
                                    }
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Box>
                </Box>
            </Container>

            <Divider sx={{ marginY: 10}}/>

            <Box
                sx={{
                    display: 'flex',
                    flexDirection: 'row',
                    justifyContent: 'space-between',
                    gap: 4,
                    width: '100%',
                    marginBottom: 8,
                }}
            >
                {/* TF-IDF Table */}
                <Box
                    sx={{
                        flex: 1,
                        borderRadius: 1,
                        backgroundColor: 'background.paper',
                        border: '1px solid',
                        borderColor: 'hsla(220, 25%, 80%, 0.2)',
                        outline: '1px solid',
                        outlineColor: 'hsla(220, 25%, 80%, 0.2)',
                        boxShadow: '0 0 12px 8px hsla(220, 25%, 80%, 0.2)',
                        padding: 2,
                        marginBottom: 4,
                    }}
                >
                    <Typography variant="h6" align="center" sx={{ marginBottom: 2 }}>
                        Ranking with TF-IDF
                    </Typography>
                    <TableContainer component={Paper}>
                        <Table>
                            <TableBody>
                                {
                                    rankedTfIdf.map((doc, index) => (
                                        <TableRow key={index}>
                                            <TableCell align="center">
                                                <Document {...doc.doc} />
                                            </TableCell>
                                        </TableRow>
                                    ))
                                }
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Box>

                {/* BM25 Table */}
                <Box
                    sx={{
                        flex: 1,
                        borderRadius: 1,
                        backgroundColor: 'background.paper',
                        border: '1px solid',
                        borderColor: 'hsla(220, 25%, 80%, 0.2)',
                        outline: '1px solid',
                        outlineColor: 'hsla(220, 25%, 80%, 0.2)',
                        boxShadow: '0 0 12px 8px hsla(220, 25%, 80%, 0.2)',
                        padding: 2,
                        marginBottom: 4,
                    }}
                >
                    <Typography variant="h6" align="center" sx={{ marginBottom: 2 }}>
                        Ranking with BM25
                    </Typography>
                    <TableContainer component={Paper}>
                        <Table>
                            <TableBody>
                                {
                                    rankedBm25.map((doc, index) => (
                                        <TableRow key={index}>
                                            <TableCell align="center">
                                                <Document {...doc.doc} />
                                            </TableCell>
                                        </TableRow>
                                    ))
                                }
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Box>
            </Box>
        </Box>
    );
}

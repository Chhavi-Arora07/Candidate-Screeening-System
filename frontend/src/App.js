import React, { useState } from 'react';
import Onboarding from './pages/Onboarding';
import Interview from './pages/Interview';
import Results from './pages/Results';

export default function App() {
  const [stage, setStage] = useState('onboarding'); // onboarding | interview | results
  const [session, setSession] = useState(null);
  const [results, setResults] = useState(null);

  const handleStart = (sessionData) => {
    setSession(sessionData);
    setStage('interview');
  };

  const handleComplete = (resultsData) => {
    setResults(resultsData);
    setStage('results');
  };

  const handleRestart = () => {
    setSession(null);
    setResults(null);
    setStage('onboarding');
  };

  return (
    <div>
      {stage === 'onboarding' && <Onboarding onStart={handleStart} />}
      {stage === 'interview' && <Interview session={session} onComplete={handleComplete} />}
      {stage === 'results' && <Results results={results} onRestart={handleRestart} />}
    </div>
  );
}

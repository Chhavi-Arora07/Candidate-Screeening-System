import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import styles from './Interview.module.css';

export default function Interview({ session, onComplete }) {
  const [question, setQuestion] = useState('');
  const [questionIndex, setQuestionIndex] = useState(0);
  const [total, setTotal] = useState(5);
  const [answer, setAnswer] = useState('');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [finishing, setFinishing] = useState(false);
  const [error, setError] = useState('');
  const textRef = useRef();

  const fetchQuestion = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getQuestion(session.session_id);
      if (data.done) {
        await finishInterview();
      } else {
        setQuestion(data.question);
        setQuestionIndex(data.question_index);
        setTotal(data.total);
      }
    } catch (e) {
      setError('Failed to load question. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const finishInterview = async () => {
    setFinishing(true);
    try {
      const results = await api.completeSession(session.session_id);
      onComplete(results);
    } catch (e) {
      setError('Failed to generate results.');
      setFinishing(false);
    }
  };

  useEffect(() => { fetchQuestion(); }, []);

  const handleSubmit = async () => {
    if (!answer.trim()) return;
    setSubmitting(true);
    setError('');
    try {
      setHistory(prev => [...prev, { q: question, a: answer }]);
      await api.submitAnswer(session.session_id, answer);
      setAnswer('');
      await fetchQuestion();
    } catch (e) {
      setError('Failed to submit answer.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSubmit();
    }
  };

  if (finishing) {
    return (
      <div className={styles.centered}>
        <div className={styles.pulse}></div>
        <p className={styles.finishText}>Generating evaluation report...</p>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <span className={styles.role}>{session.role}</span>
        <div className={styles.progress}>
          {Array.from({ length: total }).map((_, i) => (
            <div
              key={i}
              className={`${styles.dot} ${i < questionIndex ? styles.done : ''} ${i === questionIndex ? styles.active : ''}`}
            />
          ))}
        </div>
        <span className={styles.mono}>{questionIndex + 1}/{total}</span>
      </header>

      <div className={styles.content}>
        {history.length > 0 && (
          <div className={styles.history}>
            {history.slice(-2).map((item, i) => (
              <div key={i} className={styles.histItem}>
                <p className={styles.histQ}>{item.q}</p>
                <p className={styles.histA}>{item.a}</p>
              </div>
            ))}
          </div>
        )}

        <div className={styles.questionBox}>
          {loading ? (
            <div className={styles.skeleton}></div>
          ) : (
            <p className={styles.question}>{question}</p>
          )}
        </div>

        <div className={styles.answerArea}>
          <textarea
            ref={textRef}
            className={styles.textarea}
            placeholder="Type your answer here... (Ctrl+Enter to submit)"
            value={answer}
            onChange={e => setAnswer(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading || submitting}
            rows={6}
          />
          {error && <p className={styles.error}>{error}</p>}
          <div className={styles.actions}>
            <span className={styles.hint}>Ctrl+Enter to submit</span>
            <button
              className={styles.btn}
              onClick={handleSubmit}
              disabled={loading || submitting || !answer.trim()}
            >
              {submitting ? 'Submitting...' : questionIndex + 1 === total ? 'Finish →' : 'Next Question →'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

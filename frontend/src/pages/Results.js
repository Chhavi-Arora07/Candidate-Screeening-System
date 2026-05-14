import React from 'react';
import styles from './Results.module.css';

const RATING_LABELS = ['', 'Poor', 'Weak', 'Below Avg', 'Below Avg', 'Average', 'Average', 'Good', 'Strong', 'Excellent', 'Outstanding'];
const REC_COLORS = {
  'Strong Hire': '#2ed573',
  'Hire': '#7bed9f',
  'Maybe': '#ffa502',
  'No Hire': '#ff4757',
};

export default function Results({ results, onRestart }) {
  const { summary, qa_records } = results;
  const rating = summary.overall_rating || 5;
  const rec = summary.recommendation || 'Maybe';

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <header className={styles.header}>
          <span className={styles.badge}>Interview Complete</span>
          <h1 className={styles.title}>Evaluation Report</h1>
        </header>

        <div className={styles.grid}>
          {/* Score Card */}
          <div className={styles.card}>
            <p className={styles.cardLabel}>Overall Score</p>
            <div className={styles.scoreRing}>
              <span className={styles.scoreNum}>{rating}</span>
              <span className={styles.scoreDen}>/10</span>
            </div>
            <p className={styles.scoreLabel}>{RATING_LABELS[rating]}</p>
          </div>

          {/* Recommendation */}
          <div className={styles.card}>
            <p className={styles.cardLabel}>Recommendation</p>
            <div className={styles.rec} style={{ color: REC_COLORS[rec] || '#fff' }}>
              {rec}
            </div>
          </div>
        </div>

        {/* Summary */}
        <div className={styles.section}>
          <p className={styles.sectionLabel}>Summary</p>
          <p className={styles.summaryText}>{summary.summary}</p>
        </div>

        <div className={styles.twoCol}>
          {/* Strengths */}
          <div className={styles.section}>
            <p className={styles.sectionLabel}>Strengths</p>
            <ul className={styles.list}>
              {(summary.strengths || []).map((s, i) => (
                <li key={i} className={styles.listItem}>
                  <span className={styles.bullet}>+</span> {s}
                </li>
              ))}
            </ul>
          </div>

          {/* Improvements */}
          <div className={styles.section}>
            <p className={styles.sectionLabel}>Areas to Improve</p>
            <ul className={styles.list}>
              {(summary.areas_for_improvement || []).map((a, i) => (
                <li key={i} className={styles.listItem}>
                  <span className={styles.bulletMinus}>−</span> {a}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Q&A Transcript */}
        <div className={styles.section}>
          <p className={styles.sectionLabel}>Interview Transcript</p>
          <div className={styles.transcript}>
            {(qa_records || []).map((qa, i) => (
              <div key={i} className={styles.qaBlock}>
                <p className={styles.qaLabel}>Q{i + 1}</p>
                <p className={styles.qaQ}>{qa.question}</p>
                <p className={styles.qaA}>{qa.answer || <em>No answer provided</em>}</p>
              </div>
            ))}
          </div>
        </div>

        <button className={styles.btn} onClick={onRestart}>
          Start New Interview ↺
        </button>
      </div>
    </div>
  );
}

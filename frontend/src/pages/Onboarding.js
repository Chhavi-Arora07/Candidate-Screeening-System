import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import styles from './Onboarding.module.css';

export default function Onboarding({ onStart }) {
  const [roles, setRoles] = useState([]);
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getRoles().then(d => {
      setRoles(d.roles);
      setRole(d.roles[0]);
    });
  }, []);

  const handleSubmit = async () => {
    if (!name.trim() || !role || !file) {
      setError('Please fill in all fields and upload your resume.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const fd = new FormData();
      fd.append('candidate_name', name.trim());
      fd.append('role', role);
      fd.append('resume', file);
      const data = await api.startSession(fd);
      onStart(data);
    } catch (e) {
      setError('Failed to start session. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.badge}>PGAGI</div>
        <h1 className={styles.title}>AI Candidate<br />Screening</h1>
        <p className={styles.sub}>Upload your resume. Select a role. Face the machine.</p>
      </header>

      <div className={styles.card}>
        <div className={styles.field}>
          <label className={styles.label}>Full Name</label>
          <input
            className={styles.input}
            placeholder="Jane Doe"
            value={name}
            onChange={e => setName(e.target.value)}
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Target Role</label>
          <select className={styles.input} value={role} onChange={e => setRole(e.target.value)}>
            {roles.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Resume (PDF or TXT)</label>
          <label className={styles.fileBox}>
            <input
              type="file"
              accept=".pdf,.txt"
              style={{ display: 'none' }}
              onChange={e => setFile(e.target.files[0])}
            />
            <span className={styles.fileIcon}>↑</span>
            <span>{file ? file.name : 'Click to upload'}</span>
          </label>
        </div>

        {error && <p className={styles.error}>{error}</p>}

        <button
          className={styles.btn}
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? 'Analyzing resume...' : 'Begin Interview →'}
        </button>
      </div>
    </div>
  );
}

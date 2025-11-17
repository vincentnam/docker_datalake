// src/pages/Login.js
import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';

const API_BASE = 'http://localhost:5000'; // ← Change si besoin

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const history = useHistory();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Veuillez remplir tous les champs');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Appel direct sans wrapper
      const response = await fetch(`${API_BASE}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Login échoué');
      }

      // Stockage du token
      localStorage.setItem('jwtToken', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // Redirection
      history.push('/buckets');
    } catch (err) {
      setError(err.message || 'Identifiants incorrects');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Connexion</h2>

        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            type="text"
            placeholder="Nom d'utilisateur"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={styles.input}
            disabled={loading}
          />

          <input
            type="password"
            placeholder="Mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
            disabled={loading}
          />

          {error && <p style={styles.error}>{error}</p>}

          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>

        <p style={styles.footer}>
          Compte test : <code>test1</code> / <code>test</code>
        </p>
      </div>
    </div>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  card: {
    background: 'white',
    padding: '40px',
    borderRadius: '12px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
    width: '100%',
    maxWidth: '400px',
  },
  title: {
    margin: '0 0 24px',
    textAlign: 'center',
    color: '#333',
    fontSize: '28px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  input: {
    padding: '12px 16px',
    fontSize: '16px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    outline: 'none',
  },
  button: {
    padding: '14px',
    fontSize: '16px',
    fontWeight: 'bold',
    color: 'white',
    background: '#667eea',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    marginTop: '8px',
  },
  error: {
    color: '#e74c3c',
    fontSize: '14px',
    textAlign: 'center',
    margin: '0',
  },
  footer: {
    marginTop: '24px',
    textAlign: 'center',
    color: '#777',
    fontSize: '14px',
  },
};

export default Login;
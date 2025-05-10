import { useState } from 'react';
import api from '../api/axios';

export default function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState(null);

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      const resp = await api.post('/auth/register', { username, password });
      setMessage(`Utilisateur créé : ${resp.data.username}`);
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Erreur');
    }
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h2 className="text-2xl mb-4">Register</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          className="w-full p-2 border"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
        />
        <input
          type="password"
          className="w-full p-2 border"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white">
          Register
        </button>
      </form>
      {message && <p className="mt-4">{message}</p>}
    </div>
  );
}

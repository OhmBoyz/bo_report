import { useState } from 'react';
import api from '../api/axios';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState(null);

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      const resp = await api.post('/auth/token',
        new URLSearchParams({ username, password })
      );
      localStorage.setItem('access_token', resp.data.access_token);
      setMessage('Login successful');
    } catch {
      setMessage('Échec du login');
    }
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h2 className="text-2xl mb-4">Login</h2>
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
        <button type="submit" className="px-4 py-2 bg-green-600 text-white">
          Login
        </button>
      </form>
      {message && <p className="mt-4">{message}</p>}
    </div>
  );
}

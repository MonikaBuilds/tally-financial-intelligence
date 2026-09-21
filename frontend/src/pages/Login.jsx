import { useState } from 'react'
import { apiPost, setAccessToken } from '../api/client'
import './Login.css'

function Login({ onLogin }) {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [showPassword, setShowPassword] = useState(false)
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    async function handleSubmit(event) {
        event.preventDefault()

        const cleanUsername = username.trim()

        if (!cleanUsername || !password) {
            setError('Please enter your username and password.')
            return
        }

        setError('')
        setLoading(true)

        try {
            const response = await apiPost('/auth/login', {
                username: cleanUsername,
                password,
            })

            setAccessToken(response.access_token)

            sessionStorage.setItem(
                'chat_user',
                JSON.stringify({
                    user_id: response.user_id,
                    username: response.username,
                    companies: response.companies,
                }),
            )

            if (
                Array.isArray(response.companies) &&
                response.companies.length === 1
            ) {
                sessionStorage.setItem(
                    'selected_company',
                    response.companies[0],
                )
            } else {
                sessionStorage.removeItem(
                    'selected_company',
                )
            }

            onLogin?.(response)
        } catch (err) {
            setError(
                err?.message ||
                'Unable to sign in. Please verify your credentials.'
            )
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="login-page">
            <header className="login-header">
                <div className="login-header-inner">
                    <div className="login-brand">
                        <div className="login-logo">TF</div>

                        <div className="login-brand-copy">
                            <h1>Tally Financial Intelligence</h1>
                            <p>Financial Management Platform</p>
                        </div>
                    </div>

                    <div className="login-header-status">
                        <svg
                            viewBox="0 0 24 24"
                            aria-hidden="true"
                        >
                            <path
                                d="M12 3 19 6v5c0 4.6-2.9 8-7 10-4.1-2-7-5.4-7-10V6l7-3Z"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="1.8"
                            />
                            <path
                                d="m9 12 2 2 4-4"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="1.8"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                            />
                        </svg>

                        <span>Secure Access</span>
                    </div>
                </div>
            </header>

            <main className="login-main">
                <section
                    className="login-card"
                    aria-labelledby="login-title"
                >
                    <div className="login-lock">
                        <svg
                            viewBox="0 0 24 24"
                            aria-hidden="true"
                        >
                            <rect
                                x="5"
                                y="10"
                                width="14"
                                height="11"
                                rx="2"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="1.8"
                            />

                            <path
                                d="M8 10V7a4 4 0 0 1 8 0v3"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="1.8"
                                strokeLinecap="round"
                            />
                        </svg>
                    </div>

                    <div className="login-heading">
                        <h2 id="login-title">
                            Welcome back
                        </h2>

                        <p>
                            Sign in to access your financial intelligence
                            dashboard.
                        </p>
                    </div>

                    <div className="login-divider" />

                    <form
                        className="login-form"
                        onSubmit={handleSubmit}
                        noValidate
                    >
                        <div className="login-field">
                            <label htmlFor="username">
                                Username
                            </label>

                            <div className="login-input-wrapper">
                                <span className="login-input-icon">
                                    <svg
                                        viewBox="0 0 24 24"
                                        aria-hidden="true"
                                    >
                                        <circle
                                            cx="12"
                                            cy="8"
                                            r="3.5"
                                            fill="none"
                                            stroke="currentColor"
                                            strokeWidth="1.7"
                                        />

                                        <path
                                            d="M5.5 20c.4-4 2.6-6 6.5-6s6.1 2 6.5 6"
                                            fill="none"
                                            stroke="currentColor"
                                            strokeWidth="1.7"
                                            strokeLinecap="round"
                                        />
                                    </svg>
                                </span>

                                <input
                                    id="username"
                                    type="text"
                                    value={username}
                                    onChange={(event) => {
                                        setUsername(event.target.value)

                                        if (error) {
                                            setError('')
                                        }
                                    }}
                                    placeholder="Enter your username"
                                    autoComplete="username"
                                    disabled={loading}
                                    autoFocus
                                />
                            </div>
                        </div>

                        <div className="login-field">
                            <label htmlFor="password">
                                Password
                            </label>

                            <div className="login-input-wrapper">
                                <span className="login-input-icon">
                                    <svg
                                        viewBox="0 0 24 24"
                                        aria-hidden="true"
                                    >
                                        <rect
                                            x="5"
                                            y="10"
                                            width="14"
                                            height="10"
                                            rx="2"
                                            fill="none"
                                            stroke="currentColor"
                                            strokeWidth="1.7"
                                        />

                                        <path
                                            d="M8 10V7a4 4 0 0 1 8 0v3"
                                            fill="none"
                                            stroke="currentColor"
                                            strokeWidth="1.7"
                                            strokeLinecap="round"
                                        />
                                    </svg>
                                </span>

                                <input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    value={password}
                                    onChange={(event) => {
                                        setPassword(event.target.value)

                                        if (error) {
                                            setError('')
                                        }
                                    }}
                                    placeholder="Enter your password"
                                    autoComplete="current-password"
                                    disabled={loading}
                                />

                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() =>
                                        setShowPassword((current) => !current)
                                    }
                                    disabled={loading}
                                    aria-label={
                                        showPassword
                                            ? 'Hide password'
                                            : 'Show password'
                                    }
                                >
                                    {showPassword ? 'Hide' : 'Show'}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <div
                                className="login-error"
                                role="alert"
                            >
                                {error}
                            </div>
                        )}

                        <button
                            className="login-submit"
                            type="submit"
                            disabled={loading}
                        >
                            {loading && (
                                <span className="login-spinner" />
                            )}

                            {loading
                                ? 'Signing in...'
                                : 'Sign in'}
                        </button>
                    </form>

                    <div className="login-security">
                        <svg
                            viewBox="0 0 24 24"
                            aria-hidden="true"
                        >
                            <path
                                d="M12 3 19 6v5c0 4.6-2.9 8-7 10-4.1-2-7-5.4-7-10V6l7-3Z"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="1.7"
                            />

                            <path
                                d="m9 12 2 2 4-4"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="1.7"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                            />
                        </svg>

                        <span>
                            Access is restricted to authorized users.
                        </span>
                    </div>
                </section>
            </main>

            <footer className="login-footer">
                <div className="login-footer-inner">
                    <div className="footer-product">
                        <strong>
                            Tally Financial Intelligence
                        </strong>

                        <span>
                            Financial Management Platform
                        </span>
                    </div>

                    <div className="footer-meta">
                        <span>
                            © 2026 Tally Financial Intelligence
                        </span>

                        <span className="footer-separator" />

                        <span>
                            Authorized access only
                        </span>
                    </div>
                </div>
            </footer>
        </div>
    )
}

export default Login
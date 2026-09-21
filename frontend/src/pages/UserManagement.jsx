import { useEffect, useState } from 'react'
import {
  apiGet,
  apiPost,
  apiDelete,
} from '../api/client'
import PageHeader from '../components/layout/PageHeader'
import Card from '../components/common/Card'
import Loader from '../components/common/Loader'
import ErrorMessage from '../components/common/ErrorMessage'


function UserManagement() {
  const [users, setUsers] = useState([])
  const [permissions, setPermissions] = useState([])
  const [roles, setRoles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [updating, setUpdating] = useState(null)
  const [message, setMessage] = useState(null)
  const [creatingUser, setCreatingUser] = useState(false)

  const [newUser, setNewUser] = useState({
    user_id: '',
    username: '',
    password: '',
    companies: '',
    role_name: '',
  })


  async function loadAdminData() {
    setLoading(true)
    setError(null)

    try {
      const [
        usersResult,
        permissionsResult,
        rolesResult,
      ] = await Promise.all([
        apiGet('/admin/users'),
        apiGet('/admin/permissions'),
        apiGet('/admin/roles'),
      ])

      setUsers(usersResult)
      setPermissions(permissionsResult)
      setRoles(rolesResult)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadAdminData()
  }, [])


  function handleNewUserChange(event) {
    const { name, value } = event.target

    setNewUser((currentUser) => ({
      ...currentUser,
      [name]: value,
    }))
  }


  async function handleCreateUser(event) {
    event.preventDefault()

    setCreatingUser(true)
    setError(null)
    setMessage(null)

    try {
      const companyList = newUser.companies
        .split(',')
        .map((company) => company.trim())
        .filter(Boolean)

      await apiPost(
        '/admin/users',
        {
          user_id: newUser.user_id.trim(),
          username: newUser.username.trim(),
          password: newUser.password,
          companies: companyList,
          role_name: newUser.role_name,
        }
      )

      setMessage(
        `User ${newUser.username} created successfully.`
      )

      setNewUser({
        user_id: '',
        username: '',
        password: '',
        companies: '',
        role_name: '',
      })

      await loadAdminData()
    } catch (err) {
      setError(err.message)
    } finally {
      setCreatingUser(false)
    }
  }


  async function handleAssign(userId, permissionCode) {
    const operationKey =
      `${userId}-${permissionCode}`

    setUpdating(operationKey)
    setError(null)
    setMessage(null)

    try {
      await apiPost(
        `/admin/users/${encodeURIComponent(userId)}/permissions`,
        {
          permission_code: permissionCode,
        }
      )

      setMessage(
        `${permissionCode} permission assigned successfully.`
      )

      await loadAdminData()
    } catch (err) {
      setError(err.message)
    } finally {
      setUpdating(null)
    }
  }


  async function handleRemove(userId, permissionCode) {
    const operationKey =
      `${userId}-${permissionCode}`

    setUpdating(operationKey)
    setError(null)
    setMessage(null)

    try {
      await apiDelete(
        `/admin/users/${encodeURIComponent(
          userId
        )}/permissions/${encodeURIComponent(
          permissionCode
        )}`
      )

      setMessage(
        `${permissionCode} permission removed successfully.`
      )

      await loadAdminData()
    } catch (err) {
      setError(err.message)
    } finally {
      setUpdating(null)
    }
  }


  return (
    <>
      <PageHeader title="User Management" />

      {loading && <Loader />}

      {error && (
        <ErrorMessage message={error} />
      )}

      {message && (
        <div
          style={{
            marginBottom: 16,
            padding: 12,
            border: '1px solid #d1d5db',
            borderRadius: 6,
          }}
        >
          {message}
        </div>
      )}

      {!loading && (
        <>
          <Card title="Create New User">
            <form onSubmit={handleCreateUser}>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns:
                    'repeat(auto-fit, minmax(220px, 1fr))',
                  gap: 16,
                }}
              >
                <div>
                  <label htmlFor="user_id">
                    User ID
                  </label>

                  <input
                    id="user_id"
                    name="user_id"
                    type="text"
                    value={newUser.user_id}
                    onChange={handleNewUserChange}
                    required
                    disabled={creatingUser}
                    style={{
                      width: '100%',
                      marginTop: 6,
                      padding: 10,
                    }}
                  />
                </div>

                <div>
                  <label htmlFor="username">
                    Username
                  </label>

                  <input
                    id="username"
                    name="username"
                    type="text"
                    value={newUser.username}
                    onChange={handleNewUserChange}
                    required
                    disabled={creatingUser}
                    style={{
                      width: '100%',
                      marginTop: 6,
                      padding: 10,
                    }}
                  />
                </div>

                <div>
                  <label htmlFor="password">
                    Password
                  </label>

                  <input
                    id="password"
                    name="password"
                    type="password"
                    value={newUser.password}
                    onChange={handleNewUserChange}
                    required
                    minLength={8}
                    autoComplete="new-password"
                    disabled={creatingUser}
                    style={{
                      width: '100%',
                      marginTop: 6,
                      padding: 10,
                    }}
                  />
                </div>

                <div>
                  <label htmlFor="companies">
                    Companies
                  </label>

                  <input
                    id="companies"
                    name="companies"
                    type="text"
                    value={newUser.companies}
                    onChange={handleNewUserChange}
                    required
                    disabled={creatingUser}
                    placeholder="Enter company name"
                    style={{
                      width: '100%',
                      marginTop: 6,
                      padding: 10,
                    }}
                  />

                  <p className="card-note">
                    For multiple companies, separate
                    names with commas.
                  </p>
                </div>

                <div>
                  <label htmlFor="role_name">
                    Role
                  </label>

                  <select
                    id="role_name"
                    name="role_name"
                    value={newUser.role_name}
                    onChange={handleNewUserChange}
                    required
                    disabled={creatingUser}
                    style={{
                      width: '100%',
                      marginTop: 6,
                      padding: 10,
                    }}
                  >
                    <option value="">
                      Select a role
                    </option>

                    {roles.map((role) => (
                      <option
                        key={role.role_id}
                        value={role.role_name}
                      >
                        {role.role_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{ marginTop: 16 }}>
                <button
                  type="submit"
                  className="btn"
                  disabled={creatingUser}
                >
                  {creatingUser
                    ? 'Creating...'
                    : 'Create User'}
                </button>
              </div>
            </form>
          </Card>

          {!error && (
            <>
              <Card title="Users">
                {users.length === 0 ? (
                  <p className="card-note">
                    No users found.
                  </p>
                ) : (
                  users.map((user) => {
                    const isAdmin =
                      user.roles.includes('admin')

                    return (
                      <div
                        key={user.user_id}
                        style={{
                          padding: '16px 0',
                          borderBottom:
                            '1px solid #e5e7eb',
                        }}
                      >
                        <strong>
                          {user.username}
                        </strong>

                        <p className="card-note">
                          User ID: {user.user_id}
                        </p>

                        <p className="card-note">
                          Roles:{' '}
                          {user.roles.length > 0
                            ? user.roles.join(', ')
                            : 'None'}
                        </p>

                        {isAdmin ? (
                          <p className="card-note">
                            Admin has access to all
                            permission categories.
                          </p>
                        ) : (
                          <>
                            <p className="card-note">
                              Permissions:{' '}
                              {user.permissions.length > 0
                                ? user.permissions.join(', ')
                                : 'None'}
                            </p>

                            <div
                              style={{
                                display: 'flex',
                                flexWrap: 'wrap',
                                gap: 12,
                                marginTop: 12,
                              }}
                            >
                              {permissions.map(
                                (permission) => {
                                  const assigned =
                                    user.permissions.includes(
                                      permission.permission_code
                                    )

                                  const operationKey =
                                    `${user.user_id}-${permission.permission_code}`

                                  const isUpdating =
                                    updating === operationKey

                                  return (
                                    <div
                                      key={
                                        permission.permission_id
                                      }
                                      style={{
                                        border:
                                          '1px solid #e5e7eb',
                                        borderRadius: 6,
                                        padding: 12,
                                        minWidth: 180,
                                      }}
                                    >
                                      <strong>
                                        {
                                          permission.permission_name
                                        }
                                      </strong>

                                      <p className="card-note">
                                        {
                                          permission.permission_code
                                        }
                                      </p>

                                      {assigned ? (
                                        <button
                                          type="button"
                                          className="btn"
                                          disabled={isUpdating}
                                          onClick={() =>
                                            handleRemove(
                                              user.user_id,
                                              permission.permission_code
                                            )
                                          }
                                        >
                                          {isUpdating
                                            ? 'Removing...'
                                            : 'Remove'}
                                        </button>
                                      ) : (
                                        <button
                                          type="button"
                                          className="btn"
                                          disabled={isUpdating}
                                          onClick={() =>
                                            handleAssign(
                                              user.user_id,
                                              permission.permission_code
                                            )
                                          }
                                        >
                                          {isUpdating
                                            ? 'Assigning...'
                                            : 'Assign'}
                                        </button>
                                      )}
                                    </div>
                                  )
                                }
                              )}
                            </div>
                          </>
                        )}
                      </div>
                    )
                  })
                )}
              </Card>

              <Card title="Available Permissions">
                {permissions.length === 0 ? (
                  <p className="card-note">
                    No permissions found.
                  </p>
                ) : (
                  permissions.map((permission) => (
                    <div
                      key={permission.permission_id}
                      style={{
                        padding: '12px 0',
                        borderBottom:
                          '1px solid #e5e7eb',
                      }}
                    >
                      <strong>
                        {permission.permission_name}
                      </strong>

                      <p className="card-note">
                        Code:{' '}
                        {permission.permission_code}
                      </p>

                      <p className="card-note">
                        Category:{' '}
                        {permission.category}
                      </p>

                      {permission.subcategory && (
                        <p className="card-note">
                          Subcategory:{' '}
                          {permission.subcategory}
                        </p>
                      )}

                      {permission.description && (
                        <p className="card-note">
                          {permission.description}
                        </p>
                      )}
                    </div>
                  ))
                )}
              </Card>
            </>
          )}
        </>
      )}
    </>
  )
}

export default UserManagement
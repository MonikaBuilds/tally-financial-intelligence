function DataTable({ columns, rows, onRowClick, isRowClickable }) {
  if (!rows || rows.length === 0) {
    return <p className="empty-state">No records found.</p>
  }

  function rowIsClickable(row) {
    if (!onRowClick) return false
    return isRowClickable ? isRowClickable(row) : true
  }

  function handleKeyDown(event, row) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      onRowClick(row)
    }
  }

  return (
    <div className="data-table-scroll">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => {
            const clickable = rowIsClickable(row)

            return (
              <tr
                key={index}
                className={clickable ? 'data-table-row--clickable' : undefined}
                onClick={clickable ? () => onRowClick(row) : undefined}
                onKeyDown={clickable ? (event) => handleKeyDown(event, row) : undefined}
                tabIndex={clickable ? 0 : undefined}
                role={clickable ? 'button' : undefined}
              >
                {columns.map((column) => (
                  <td key={column.key}>
                    {column.render ? column.render(row) : row[column.key]}
                  </td>
                ))}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default DataTable
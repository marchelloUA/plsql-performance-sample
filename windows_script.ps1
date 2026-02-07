# windows_script.ps1
param (
    [string]$Server = "localhost",
    [string]$Database = "master",
    [string]$Query
)

function Invoke-SqlQuery {
    param($server, $database, $query)
    
    $connectionString = "Server=$server;Database=$database;User Id=sa;Password=YourStrongPassword123!"
    $connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
    $command = $connection.CreateCommand()
    $command.CommandText = $query
    
    try {
        $connection.Open()
        $result = $command.ExecuteReader()
        $table = @()
        while ($result.Read()) {
            $row = @{
                ServerName = $result[0]
                DatabaseName = $result[1]
                Version = $result[2]
            }
            $table += $row
        }
        return $table
    }
    finally {
        $connection.Close()
    }
}

# Query SQL Server from PowerShell
$query = "SELECT @@SERVERNAME as ServerName, DB_NAME() as DatabaseName, @@VERSION as Version"
$result = Invoke-SqlQuery -Server $Server -Database $Database -Query $query
$result | Format-Table
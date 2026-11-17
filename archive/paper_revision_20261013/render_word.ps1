param([Parameter(Mandatory=$true)][string]$InputDocx, [Parameter(Mandatory=$true)][string]$OutputPdf)
$ErrorActionPreference = 'Stop'
$sourcePath = [IO.Path]::GetFullPath($InputDocx)
$pdfPath = [IO.Path]::GetFullPath($OutputPdf)
if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) { throw 'Input missing' }
New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($pdfPath)) -Force | Out-Null
$wordRenderer = $null
$wordDocument = $null
try {
    $wordRenderer = New-Object -ComObject Word.Application
    $wordRenderer.Visible = $false
    $wordRenderer.DisplayAlerts = 0
    $wordRenderer.AutomationSecurity = 3
    $wordDocument = $wordRenderer.Documents.Open($sourcePath, $false, $true)
    $wordDocument.ExportAsFixedFormat($pdfPath, 17)
    Write-Output ('Rendered PDF: ' + $pdfPath)
} finally {
    if ($null -ne $wordDocument) { $wordDocument.Close($false); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordDocument) }
    if ($null -ne $wordRenderer) { $wordRenderer.Quit(); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordRenderer) }
}

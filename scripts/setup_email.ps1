Param(
  [Parameter(Mandatory = $false)]
  [string]$EnvPath = "$(Resolve-Path (Join-Path $PSScriptRoot '..'))\.env"
)

$ErrorActionPreference = "Stop"

Write-Host "INBOTF - Configuracion de correo SMTP" -ForegroundColor Cyan
Write-Host "Se creara/actualizara: $EnvPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "Recomendado (Gmail): usa App Password (no tu contrasena normal)." -ForegroundColor Yellow
Write-Host ""

$hostInput = Read-Host "SMTP Host (Enter para smtp.gmail.com)"
if ([string]::IsNullOrWhiteSpace($hostInput)) { $hostInput = "smtp.gmail.com" }

$portInput = Read-Host "SMTP Port (Enter para 587)"
if ([string]::IsNullOrWhiteSpace($portInput)) { $portInput = "587" }

$tlsInput = Read-Host "Usar TLS? (true/false, Enter para true)"
if ([string]::IsNullOrWhiteSpace($tlsInput)) { $tlsInput = "true" }

$user = Read-Host "Correo remitente (DJANGO_EMAIL_HOST_USER)"
if ([string]::IsNullOrWhiteSpace($user)) { throw "Debes ingresar un correo remitente." }

$passSecure = Read-Host "Contrasena SMTP / App Password" -AsSecureString
$passPtr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($passSecure)
try {
  $passPlain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($passPtr)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passPtr) | Out-Null
}
if ([string]::IsNullOrWhiteSpace($passPlain)) { throw "Debes ingresar una contrasena/app password." }

$defaultFrom = Read-Host "DEFAULT_FROM (Enter para INBOTF <${user}>)"
if ([string]::IsNullOrWhiteSpace($defaultFrom)) { $defaultFrom = "INBOTF <$user>" }

$timeout = Read-Host "Timeout segundos (Enter para 15)"
if ([string]::IsNullOrWhiteSpace($timeout)) { $timeout = "15" }

$content = @"
# Archivo local de variables de entorno (NO se sube a git)
DJANGO_EMAIL_HOST=$hostInput
DJANGO_EMAIL_PORT=$portInput
DJANGO_EMAIL_USE_TLS=$tlsInput
DJANGO_EMAIL_HOST_USER=$user
DJANGO_EMAIL_HOST_PASSWORD=$passPlain
DJANGO_DEFAULT_FROM_EMAIL=$defaultFrom
DJANGO_EMAIL_TIMEOUT=$timeout
"@

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $EnvPath) | Out-Null
Set-Content -Path $EnvPath -Value $content -Encoding UTF8

Write-Host ""
Write-Host "Listo. .env creado/actualizado." -ForegroundColor Green
Write-Host "Ahora reinicia el servidor Django para que cargue las variables." -ForegroundColor Green


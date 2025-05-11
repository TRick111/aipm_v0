#requires -Version 5.0
<##
setup_workspace_simple.ps1
AIプロジェクト管理ワークスペースの簡易構築スクリプト (PowerShell版)

使い方:
  .\setup_workspace_simple.ps1 [root_directory] [config_file]
  .\setup_workspace_simple.ps1 [config_file]

例:
  .\setup_workspace_simple.ps1 C:\Users\username\new_workspace .\my_config.ps1
  .\setup_workspace_simple.ps1 setup_config.ps1

- 基本的なフォルダ構造を作成し、Flowに日付フォルダを作成します
- configファイルを指定すると、クローンするリポジトリをカスタマイズできます
- Windows PowerShell/PowerShell Core対応
##>

param(
  [string]$RootDir = '.',
  [string]$ConfigFile = './setup_config.ps1'
)

# 色定義
$ColorMap = @{ Info = 'Cyan'; Success = 'Green'; Warning = 'Yellow'; Error = 'Red' }
function Write-Log($msg, $type = 'Info') {
  $color = $ColorMap[$type]
  Write-Host "[$type] $msg" -ForegroundColor $color
}

# デフォルト設定
$RULE_REPOS = @( 'https://github.com/miyatti777/rules_basic_public.git|.cursor/rules/basic' )
$SCRIPT_REPOS = @( 'https://github.com/miyatti777/scripts_public.git|scripts' )
$PROGRAM_REPOS = @( 'https://github.com/miyatti777/sample_pj_curry.git|Stock/programs/夕食作り' )
$SAMPLE_PROGRAMS = @( '夕食作り' )
$BASE_DIRS = @( 'Flow','Stock','Archived','Archived/projects','scripts','.cursor/rules','.cursor/rules/basic','Stock/programs' )
$AUTO_APPROVE = $false
$AUTO_CLONE = $false

# 設定ファイルの読み込み
function Import-Config {
  param([string]$file)
  if (Test-Path $file) {
    Write-Log "コンフィグファイルを読み込んでいます: $file" 'Info'
    . $file
    Write-Log "コンフィグファイルを読み込みました" 'Success'
  } else {
    Write-Log "指定されたコンフィグファイルが見つかりません: $file" 'Warning'
    Write-Log "デフォルト設定を使用します" 'Info'
  }
}

# Gitリポジトリのクローン
function Clone-Repository {
  param($url, $target)
  $fullPath = Join-Path $RootDir $target
  if (Test-Path (Join-Path $fullPath '.git')) {
    Write-Log "リポジトリは既に存在します: $target - 更新を試みます" 'Info'
    Push-Location $fullPath; git pull; Pop-Location
    Write-Log "リポジトリを更新しました: $target" 'Success'
  } else {
    if (Test-Path $fullPath) {
      if ((Get-ChildItem $fullPath -Force | Measure-Object).Count -gt 0) {
        Write-Log "ターゲットディレクトリ '$fullPath' は空ではありません。クローンできません。" 'Error'
        return
      }
      Remove-Item $fullPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path (Split-Path $fullPath) -Force | Out-Null
    Write-Log "リポジトリをクローンしています: $url -> $target" 'Info'
    git clone $url $fullPath
    if ($LASTEXITCODE -eq 0) {
      Write-Log "リポジトリをクローンしました: $target" 'Success'
    } else {
      Write-Log "リポジトリのクローンに失敗しました: $url" 'Error'
    }
  }
}

function Clone-Repositories {
  Write-Log "リポジトリをクローンしています..." 'Info'
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Log "git がインストールされていません。リポジトリクローンをスキップします。" 'Warning'
    return
  }
  $doClone = $true
  if (-not $AUTO_CLONE) {
    $ans = Read-Host 'リポジトリをクローンしますか？ (y/n)'
    if ($ans -notin @('y','Y')) { $doClone = $false }
  } else {
    Write-Log "AUTO_CLONE=true が設定されているため、すべてのリポジトリを自動クローンします" 'Info'
  }
  if ($doClone) {
    foreach ($repo in $RULE_REPOS) {
      $url, $target = $repo -split '\|',2
      Clone-Repository $url $target
    }
    foreach ($repo in $SCRIPT_REPOS) {
      $url, $target = $repo -split '\|',2
      Clone-Repository $url $target
    }
    foreach ($repo in $PROGRAM_REPOS) {
      $url, $target = $repo -split '\|',2
      $repoDo = $true
      if (-not $AUTO_CLONE) {
        $ans2 = Read-Host "$url をクローンしますか？ (y/n)"
        if ($ans2 -notin @('y','Y')) { $repoDo = $false }
      }
      if ($repoDo) {
        try { Clone-Repository $url $target } catch { Write-Log "リポジトリ $url のクローンに問題が発生しましたが、処理は継続します" 'Warning' }
      } else {
        Write-Log "リポジトリはスキップされました: $url" 'Info'
      }
    }
    Write-Log "リポジトリのクローンが完了しました" 'Success'
  } else {
    Write-Log "リポジトリのクローンはスキップされました" 'Info'
  }
}

function Create-FallbackDirectories {
  Write-Log "追加のディレクトリを作成しています..." 'Info'
  $common = Join-Path $RootDir 'Stock/programs/Common/Public'
  if (-not (Test-Path $common)) {
    New-Item -ItemType Directory -Path $common -Force | Out-Null
    Write-Log "共通ナレッジディレクトリ作成: Stock/programs/Common/Public" 'Info'
  }
  foreach ($prog in $SAMPLE_PROGRAMS) {
    $progDir = Join-Path $RootDir "Stock/programs/$prog"
    if (-not (Test-Path $progDir)) {
      New-Item -ItemType Directory -Path $progDir -Force | Out-Null
      Write-Log "プログラムディレクトリ作成: Stock/programs/$prog" 'Info'
    }
  }
}

function Setup-VSCodeSettings {
  Write-Log "VSCode設定を更新しています..." 'Info'
  $vscodeDir = Join-Path $RootDir '.vscode'
  if (-not (Test-Path $vscodeDir)) { New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null }
  $settingsJson = Join-Path $vscodeDir 'settings.json'
  $marpSetting = '{`n  "markdown.marp.themes": [`n    ".cursor/rules/basic/templates/marp-themes/explaza.css",`n    ".cursor/rules/basic/templates/marp-themes/modern-brown.css"`n  ]`n}'
  if (Test-Path $settingsJson) {
    $content = Get-Content $settingsJson -Raw
    if ($content -match 'markdown.marp.themes') {
      Write-Log "markdown.marp.themes の設定はすでに存在します。スキップします。" 'Info'
    } else {
      $content = $content.TrimEnd('}') + ",`n  " + $marpSetting.Trim('{','}') + "`n}"
      Set-Content $settingsJson $content
      Write-Log "settings.jsonにマープテーマ設定を追加しました" 'Success'
    }
  } else {
    Set-Content $settingsJson $marpSetting
    Write-Log "settings.jsonを新規作成しました" 'Success'
  }
}

function Update-MarpThemePaths {
  Write-Log "マープテーマのパスを更新しています..." 'Info'
  $themeDir = Join-Path $RootDir '.cursor/rules/basic/templates/marp-themes'
  if (-not (Test-Path $themeDir)) {
    Write-Log "テーマディレクトリが見つかりません: $themeDir" 'Warning'
    return
  }
  $newPath = Join-Path $themeDir 'assets'
  Get-ChildItem $themeDir -Filter *.css | ForEach-Object {
    $cssPath = $_.FullName
    $content = Get-Content $cssPath -Raw
    $newContent = $content -replace 'background-image: url\("[^"]*assets/', "background-image: url(`"$newPath/"
    Set-Content $cssPath $newContent
    Write-Log "更新: $cssPath" 'Info'
  }
  Write-Log "マープテーマの背景画像パスを更新しました" 'Success'
}

# メイン処理
function Main {
  Write-Host '============================================================'
  Write-Host '     AIプロジェクト管理ワークスペース簡易構築スクリプト'
  Write-Host '============================================================'
  # 引数処理
  if ($args.Count -eq 1 -and $args[0] -like '*.ps1') {
    $script:RootDir = '.'
    $script:ConfigFile = $args[0]
  } elseif ($args.Count -ge 1) {
    $script:RootDir = $args[0]
    $script:ConfigFile = if ($args.Count -ge 2) { $args[1] } else { './setup_config.ps1' }
  }
  # 設定ファイル読み込み
  Import-Config $ConfigFile
  $script:RootDir = (Resolve-Path $RootDir).Path
  Write-Log "ワークスペースのルートディレクトリ: $RootDir" 'Info'
  Write-Log "使用するコンフィグファイル: $ConfigFile" 'Info'
  if (-not $AUTO_APPROVE) {
    $ans = Read-Host 'この場所にワークスペースを作成してよろしいですか？ (y/n)'
    if ($ans -notin @('y','Y')) {
      Write-Log 'キャンセルされました' 'Info'
      exit 0
    }
  } else {
    Write-Log 'AUTO_APPROVE=true が設定されているため、確認をスキップします' 'Info'
  }
  if (-not (Test-Path $RootDir)) { New-Item -ItemType Directory -Path $RootDir -Force | Out-Null }
  Write-Log '基本ディレクトリ構造を作成しています...' 'Info'
  foreach ($dir in $BASE_DIRS) {
    $d = Join-Path $RootDir $dir
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
    Write-Log "ディレクトリ作成: $dir" 'Info'
  }
  # 日付フォルダ作成
  $today = Get-Date -Format 'yyyy-MM-dd'
  $yearMonth = Get-Date -Format 'yyyyMM'
  $flowDateDir = Join-Path $RootDir "Flow/$yearMonth/$today"
  if (-not (Test-Path $flowDateDir)) { New-Item -ItemType Directory -Path $flowDateDir -Force | Out-Null }
  Write-Log "日付フォルダ作成: Flow/$yearMonth/$today" 'Info'
  # リポジトリのクローン
  Clone-Repositories
  # クローンされなかったディレクトリをフォールバックとして作成
  Create-FallbackDirectories
  # VSCode設定を更新
  Setup-VSCodeSettings
  # マープテーマのパスを更新
  Update-MarpThemePaths
  Write-Log "ワークスペースの構築が完了しました: $RootDir" 'Success'
  Write-Host '============================================================'
  Write-Host '完了しました！新しいワークスペースが構築されました。'
  Write-Host "ディレクトリ: $RootDir"
  Write-Host '============================================================'
}

Main $args 
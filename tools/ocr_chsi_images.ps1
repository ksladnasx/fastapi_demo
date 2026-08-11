Add-Type -AssemblyName System.Runtime.WindowsRuntime

[void][Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
[void][Windows.Storage.Streams.IRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
[void][Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
[void][Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
[void][Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]

$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
})[0]

function Await-Operation($Operation, [Type]$ResultType) {
    $task = $asTask.MakeGenericMethod($ResultType).Invoke($null, @($Operation))
    $task.Wait()
    return $task.Result
}

function Read-OcrText($ImagePath, $Engine) {
    $file = Await-Operation ([Windows.Storage.StorageFile]::GetFileFromPathAsync($ImagePath)) ([Windows.Storage.StorageFile])
    $stream = Await-Operation ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $decoder = Await-Operation ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bitmap = Await-Operation ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $result = Await-Operation ($Engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
    return $result.Text
}

$inputPath = (Resolve-Path $args[0]).Path
$outputPath = $args[1]
$utf8 = [System.Text.UTF8Encoding]::new($false)
$rows = [System.IO.File]::ReadAllText($inputPath, $utf8) | ConvertFrom-Json
$language = [Windows.Globalization.Language]::new('zh-CN')
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($language)
if ($null -eq $engine) {
    throw 'Windows OCR engine could not be created for zh-CN.'
}

$results = New-Object System.Collections.Generic.List[object]
foreach ($row in $rows) {
    $paths = @($row.localImagePaths -split "`n" | Where-Object { $_ -and $_.Trim() })
    $urls = @($row.imageUrls -split "`n")
    for ($i = 0; $i -lt $paths.Count; $i++) {
        $imagePath = (Resolve-Path -LiteralPath $paths[$i]).Path
        try {
            $text = Read-OcrText $imagePath $engine
            $status = '成功'
            $errorMessage = ''
        } catch {
            $text = ''
            $status = '失败'
            $errorMessage = $_.Exception.Message
        }
        $results.Add([PSCustomObject]@{
            school = $row.school
            year = $row.year
            imageIndex = $i + 1
            imageUrl = if ($i -lt $urls.Count) { $urls[$i] } else { '' }
            localImagePath = $imagePath
            articleUrl = $row.articleUrl
            status = $status
            error = $errorMessage
            ocrText = ($text -replace "\s+", ' ').Trim()
        }) | Out-Null
        Write-Host ("{0} #{1} {2}" -f $row.school, ($i + 1), $status)
    }
}

$json = $results | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText((Resolve-Path -LiteralPath (Split-Path -Parent $outputPath)).Path + '\' + (Split-Path -Leaf $outputPath), $json, $utf8)

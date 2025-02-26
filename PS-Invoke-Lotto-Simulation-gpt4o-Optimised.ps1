param (
    [string]$drawName = "euromillions",
    [string]$simulateDraw = "yes"
)

Switch ($drawName) {
    "euromillions" {
        $ballsDrawn = 5
        $specialBallsDrawn = 2
        $maxDrawNumber = 50
        $maxSpecialDrawNumber = 12
    }
    "lotto" {
        $ballsDrawn = 6
        $specialBallsDrawn = 0
        $maxDrawNumber = 59
        $maxSpecialDrawNumber = 0
    }
    "thunderball" {
        $ballsDrawn = 5
        $specialBallsDrawn = 1
        $maxDrawNumber = 39
        $maxSpecialDrawNumber = 14
    }
    "setforlife" {
        $ballsDrawn = 5
        $specialBallsDrawn = 1
        $maxDrawNumber = 47
        $maxSpecialDrawNumber = 10
    }
    Default {
        Write-Error "Invalid draw name: $drawName"
    }
}

function Get-Draw {
    $numbers = 1..$maxDrawNumber | Get-Random -Count $ballsDrawn
    $specialNumbers = if ($specialBallsDrawn -gt 0) { 1..$maxSpecialDrawNumber | Get-Random -Count $specialBallsDrawn } else { @() }
    $drawResult = $numbers + $specialNumbers
    $drawResult
}

function Get-LD {
    $numbers = 1..$maxDrawNumber | Get-Random -Count $ballsDrawn
    $specialNumbers = if ($specialBallsDrawn -gt 0) { 1..$maxSpecialDrawNumber | Get-Random -Count $specialBallsDrawn } else { @() }
    $luckyDipResult = $numbers + $specialNumbers
    $luckyDipResult
}

Function invoke-DrawSimulation {
    $win = 0
    $cnt = 0
    $starttm = Get-Date
    $drawCollisionObject = (Get-Draw | Sort-Object).ForEach({ $_.ToString("D2") }) -join ':'

    while ($win -eq 0) {
        $ldCollisionObject = (Get-LD | Sort-Object).ForEach({ $_.ToString("D2") }) -join ':'

        if ($drawCollisionObject -eq $ldCollisionObject) {
            Write-Output "MATCH: Try number $cnt $drawCollisionObject---$ldCollisionObject"
            $win++
            $endtm = Get-Date
            $timetaken = New-TimeSpan -Start $starttm -End $endtm
            Set-Content -Path ".\log\winner.txt" -Value "Winning value of $drawCollisionObject---$ldCollisionObject for a DRAW vs Lucky Dip. Try number $cnt, it only took $($timetaken.Days) days, $($timetaken.Hours) hours, $($timetaken.Minutes) minutes and $($timetaken.Seconds) seconds." -Force
            exit 0
        } else {
            $cnt++
            Write-Output "NO-MATCH: Try number $cnt $drawCollisionObject---$ldCollisionObject"
        }
    }
}

if ($simulateDraw -ilike "y*") {
    invoke-DrawSimulation
} else {
    Get-LD
}

Get-Variable -Exclude PWD,*Preference | Remove-Variable -EA 0
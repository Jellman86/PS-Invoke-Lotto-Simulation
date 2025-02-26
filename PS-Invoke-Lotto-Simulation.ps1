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

    # Format the numbers
    $formattedNumbers = $numbers | ForEach-Object { '{0:d2}' -f $_ }

    $drawResult = @()
    for ($i = 0; $i -lt $ballsDrawn; $i++) {
        $drawResult += [pscustomobject]@{Number=$formattedNumbers[$i]; Ball=($i + 1).ToString()}
    }

    if ($specialBallsDrawn -gt 0) {
        $specialNumbers = 1..$maxSpecialDrawNumber | Get-Random -Count $specialBallsDrawn
        $formattedSpecialNumbers = $specialNumbers | ForEach-Object { '{0:d2}' -f $_ }
        for ($i = 0; $i -lt $specialBallsDrawn; $i++) {
            $drawResult += [pscustomobject]@{Number=$formattedSpecialNumbers[$i]; Ball='LS'}
        }
    }

    $drawResult | Sort-Object Number
}

function Get-LD {
    $numbers = 1..$maxDrawNumber | Get-Random -Count $ballsDrawn

    # Format the numbers
    $formattedNumbers = $numbers | ForEach-Object { '{0:d2}' -f $_ }

    $luckyDipResult = @()
    for ($i = 0; $i -lt $ballsDrawn; $i++) {
        $luckyDipResult += [pscustomobject]@{Number=$formattedNumbers[$i]; Ball=($i + 1).ToString()}
    }

    if ($specialBallsDrawn -gt 0) {
        $specialNumbers = 1..$maxSpecialDrawNumber | Get-Random -Count $specialBallsDrawn
        $formattedSpecialNumbers = $specialNumbers | ForEach-Object { '{0:d2}' -f $_ }
        for ($i = 0; $i -lt $specialBallsDrawn; $i++) {
            $luckyDipResult += [pscustomobject]@{Number=$formattedSpecialNumbers[$i]; Ball='LS'}
        }
    }

    $luckyDipResult | Sort-Object Number
}

Function invoke-DrawSimulation {
        $win = 0
        $cnt = 0
        $starttm = Get-Date
        $drawCollisionObject = (([string](Get-Draw | Sort-Object Number).Number)).Replace(" ", ":")

        while($win -ieq '0'){

            $ldCollisionObject = (([string](Get-LD | Sort-Object Number).Number)).Replace(" ", ":")

            if($drawCollisionObject -eq $ldCollisionObject){
                "MATCH: Try number (d1)$drawCollisionObject---(ld)$ldCollisionObject"  
                $win++
                $endtm = Get-Date
                $timetaken = New-TimeSpan -Start $starttm -End $endtm
                $tmdays = $timetaken.Days
                $tmhours = $timetaken.Hours
                $tmmins = $timetaken.Minutes
                $tmsecs = $timetaken.Seconds
                Set-Content -Path ".\log\winner.txt" -Value "Winning value of (d1)$drawCollisionObject---(ld)$ldCollisionObject for a DRAW vs Lucky Dip. Try number $cnt, it only took $tmdays days, $tmhours hours, $tmmins minuites and $tmsecs seconds." -Force
                exit 0
            }else{
                $cnt++ 
                "NO-MATCH: Try number $cnt, (d1)$drawCollisionObject---(ld)$ldCollisionObject"     
            }
        }
}

if($simulateDraw -ilike "y*"){
    invoke-DrawSimulation;
}else{
    get-ld;
}

Get-Variable -Exclude PWD,*Preference | Remove-Variable -EA 0
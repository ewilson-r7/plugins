# silentlycontinue inside the exec-retry negates the exec-retry since silentlycontinue will cause the command to not throw an exception, which is what exec-retry is relying on to detect errors it should retry.
# In other words, don't use silentlycontinue if you want this fuction to behave as expected.    If the behavior is not as expected, add -ErrorAction Stop to the command you pass in. 
function Backoff-Retry-Wrapper {
    param(
        [string]$command,
        [int]$total_tries = 6,
        [int]$initial_timer = 15,
        [int]$final_timer = 30,
        [int]$initial_tries = 3,
        [ref]$output
    )
    $count=0
    $timeout=$initial_timer
    while($count -lt $total_tries){
        if ($count -ge $initial_tries) {
            write-warning "backing off retry rate"
            #short timeouts are over- back off to the longer timeouts
            $timeout=$final_timer
        }
        try {
            #considered using -OutVariable but PS 6.0 will be changing the type so didn't want to get mixed into that
            $output.Value = Invoke-Expression -ErrorVariable errors $command -ErrorAction Stop
            return
        } catch {
            write-warning "attempt $count failed for $command"
            write-warning $_.Exception
            Start-Sleep -Seconds $timeout
            $count+=1
        }
    }
    throw "Ran $command $tries times and failed every time.    Last execution attempt error was $errors"
}

function Exec-Retry {
    param (
        [string]$command,
        [ref]$output= 0,
        [int]$tries= 6
    )
        Backoff-Retry-Wrapper $command -output $output -total_tries $tries
}

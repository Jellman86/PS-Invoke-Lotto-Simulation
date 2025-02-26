# PS-Invoke-Lotto-Simulation

Powershell Script to generate lottery random numbers and also run a lottery simulation.

Ive always been interested in the question that if initial conditions are identical could you simulate ahead of time, the lottery numbers that are about to be drawn. While this little script goes no where near answering that Idea, the simulation may give you an idea of quite how unlikley a lottery win is! 

## Usage

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/PS-Invoke-Lotto-Simulation.git
    cd PS-Invoke-Lotto-Simulation
    ```

2. **Run the script**:
    ```sh
    .\PS-Invoke-Lotto-Simulation.ps1 -drawName <drawName> -simulateDraw <yes/no>
    ```

### Parameters

- `-drawName`: Specifies the type of lottery draw. Possible values are:
  - `euromillions`
  - `lotto`
  - `thunderball`
  - `setforlife`

- `-simulateDraw`: Specifies whether to run a simulation. Possible values are:
  - `yes`: Runs the simulation to find a matching draw and lucky dip.
  - `no`: Generates a lucky dip without running the simulation.

### Examples

1. **Generate a EuroMillions lucky dip**:
    ```sh
    .\PS-Invoke-Lotto-Simulation.ps1 -drawName euromillions -simulateDraw no
    ```

2. **Run a simulation for Lotto**:
    ```sh
    .\PS-Invoke-Lotto-Simulation.ps1 -drawName lotto -simulateDraw yes
    ```

### Output

- If `-simulateDraw` is set to `yes`, the script will run a simulation and log the results in `.\log\winner.txt`.
- If `-simulateDraw` is set to `no`, the script will output the lucky dip numbers to the console.

## Requirements

- PowerShell 5.1 or later

## License

This is licensed under the MIT License.
# Sola-board-game

## Installation

- Connect via SSH to the RPi:
```
ssh  admin@qudev-rpi-graham-hat.dhcp-int.phys.ethz.ch
```

- Install prerequisites on RPi

```
sudo apt-get install -y i2c-tools libgpiod-dev python3-smbus python3-pil fonts-dejavu python3-dev
```

- Enable [I2C](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c) and SPI

- Clone this repository to `/home/admin` (or 
setup a remote interpreter and FSTP file transfer via 
PyCharm remote projects).

- Create a virtual environment

    ```
    python3 -m venv ~/phdhatenv
    ```

- Enable the virtual env

    ```
    source ~/phdhatenv/bin/activate
    ```

_Hint: This gets activated automagically in the `phd-hat.service`_

- Install python package & dependencies

    ```
    cd ~/sola-board-game
    pip install -e .
    ```

## Running

For testing

```
sudo /home/admin/phdhatenv/bin/python /home/admin/sola-board-game/src/surface_board_game/main.py
```

As a systemd service

```
sudo cp phd-hat.service /etc/systemd/system/phd-hat.service
sudo systemctl daemon-reload
sudo systemctl enable phd-hat.service
sudo systemctl start phd-hat.service
```

## Troubleshooting

- Enable linger for the `admin` user:

    ```
    sudo loginctl enable-linger admin
    ```

This ensures the user manager is started at boot. All services the user has created will get started then, too.

So in case you added the `phd-hat-service` to the `admin` user, it will get started. This installation procedure, however, adds it to the system.

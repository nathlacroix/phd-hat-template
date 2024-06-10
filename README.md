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

- Enable linger for the `admin` user (ensures not to kill services after logging off):

    ```
    sudo systemctl enable-linger admin
    ```
    EDIT: NL:
    the command above did not work for me, I used:
    ```
    sudo loginctl enable-linger admin
    ```
- Create a virtual environment

    ```
    python3 -m venv ~/phdhatenv
    ```

- Clone this repository to `/home/admin` (or 
setup a remote interpreter and FSTP file transfer via 
PyCharm remote projects).

- Install python package
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
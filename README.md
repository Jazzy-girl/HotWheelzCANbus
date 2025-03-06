# HotWheelzCANbus

Theoretical code for the Raspberry Pi for interpreting BMS CANbus data and uploading it to a monitor for the driver.

# Developers

Divna Mijić
Ryanne Wilson

# Necessary Installs

can
cantools
tkinter

# How to import:

## 1. Install cantools (Python CAN library)

### Linux

sudo apt install python3-can

### Windows

pip install can (maybe?)

### Macbook (if using Homebrew)

1. Firstly, install python if you don't already have it

```bash
brew install python
```

2. Then, install python-can and cantools via pip:

```bash
pip3 install python-can cantools
```

## 2. Install tkinter (GUI library)

### Linux

```bash
sudo apt install python3-can
```

### Windows

```bash
pip install can (maybe?)
```

### Macbook (if using Homebrew)

```bash
 brew install python-tk
```

Unless you are using avirtual machine, your laptop will likely complain. To bypass this issue and force install tkinter locally on yoru computer run the following:

```bash
pip3 install --break-system-packages python-can cantools
```

## 3. Install opencv

By running this command, you are installing dependencies needed to use the Raspberry Pi camera

### Virtual Machine

```bash
???
```

### Linux

```bash
sudo apt install python3-can
```

### Windows

```bash
pip install can (maybe?)
```

### Macbook (if using Homebrew)

```bash
 brew install python-tk
```

## 4. Running

Just run the ReceivingDataCode.py as you normally would, a display window will open with simple GUI

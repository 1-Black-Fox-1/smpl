# Simple Player

<img src="https://github.com/1-Black-Fox-1/smpl/blob/main/src/resources/images/simple-player.png" width="200">

Cross-platform local music player written in python with [kivy](https://github.com/kivy/kivy) framework

![python versions](https://camo.githubusercontent.com/426157aa08cc06f064a8360f4d4220b741e8438066df1bb5c65aa1430bc8225c/68747470733a2f2f696d672e736869656c64732e696f2f707970692f707976657273696f6e732f6b697679)

## Warning

The project is still in active development  
Expect bugs and breaking changes

## Requirements

- Python with venv installed
- Git

## Run without building

### Windows(Powershell)

```ps1
git clone https://github.com/1-Black-Fox-1/smpl
cd smpl
python -m venv src\venv
.\src\venv\Scripts\Activate.ps1
pip install -r requirements-win.txt
python src\asyncmain.py
```

### Linux

```bash
git clone https://github.com/1-Black-Fox-1/smpl
cd smpl
python -m venv src/venv
source src/venv/bin/activate
pip install -r requirements.txt
python src/asyncmain.py
```

## Building

### Windows(Powershell)

```ps1
git clone https://github.com/1-Black-Fox-1/smpl
cd smpl
python -m venv src\venv
src\venv\Scripts\pip install -r requirements-win.txt
.\scripts\build.ps1
```

### Linux

```bash
git clone https://github.com/1-Black-Fox-1/smpl
cd smpl
python -m venv src/venv
src/venv/bin/pip install -r requirements.txt
chmod +x ./scripts/build.sh
./scripts/build.sh
# if you want .desktop file
chmod +x ./scripts/create-desktop-entry.sh
./scripts/create-desktop-entry.sh
```

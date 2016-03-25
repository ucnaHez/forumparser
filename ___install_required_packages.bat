for /f "tokens=*" %%a in (___required_packages.txt) do (
	pip install %%a
)
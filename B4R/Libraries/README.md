# B4R Additional Libraries

This folder contains external B4R libraries required for specific experiments in the **Hawe** project.  
These libraries must be present in your **B4R additional libraries path** to ensure successful compilation and deployment.

> **Note:** B4R does not automatically download dependencies. You must manually copy required libraries to the appropriate folder, typically found at:  
> `Documents\B4X\AdditionalLibraries\B4R\Libraries`

---

## Included Dependencies

| Experiment       | Required Library |
|------------------|------------------|
| `hawe_sht20`     | `rSHT20`         |

---

## How to Use

1. Download or clone this repository.
2. Copy the contents of this folder to your B4R Additional Libraries folder:
   - **Windows default**: `C:\Users\<YourName>\Documents\B4X\AdditionalLibraries\B4R\Libraries`
3. Restart the B4R IDE if it was open.
4. Open the related experiment (e.g., `hawe_sht20`) and compile.

---

## Creating Your Own Library

If you're building a custom experiment that uses a C++ library, you can wrap it using a `.h` and `.cpp` file pair and expose it through the B4R community.
See existing libraries like `rSHT20` as a reference.

---

## Credits

Special thanks to the **B4X community** and contributors of open-source Arduino-compatible libraries used within this project.

Read more about [B4R](https://www.b4x.com/b4r.html) - Easily build native Arduino & ESP8266 programs.

---

## License

Unless otherwise noted, all libraries are subject to their original licenses. Please check individual `.h` or `.cpp` files for license headers or documentation.

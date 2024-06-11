<h1><img class="dark-light" src="doc/_static/logo_horizontal.png" style="width: 30%;"></h1>
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)
![example snapshot](doc/resources/example_snapshot.png)  
An open source interactive spectrogram audio player, primarily based on bokeh and the holoviz stack (wav+holoviz=waloviz).
## How to use?
In jupyter\jupyterlab:
```python
import waloviz as wv
wv.extension()
wv.Audio('http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3')
```
I am actively working on making this project a publicly available pip package with doc and CI/CD etc,  
some really exciting stuff :)  

## A VERY initial Roadmap
 - [x] reserve domains\handles\etc.
 - [x] become open source
 - [ ] make the repo welcoming for users and contributors
 - [ ] make a github actions CI/CD pipeline
 - [ ] publish a test package
 - [ ] make sure that everything works OOTB
 - [ ] publish an alpha package
 - [ ] make sure that everything works again
 - [ ] create a documentation website with an interactive example
 - [ ] document everything
 - [ ] go through every link and make sure it works properly
 - [ ] create known issues
 - [ ] create a more advanced roadmap
 - [ ] launch the package on social media

## Contributing
Please read the [CONTRIBUTING](CONTRIBUTING.md) guidelines and our [CODE OF CONDUCT](CODE_OF_CONDUCT.md).
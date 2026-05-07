# GridFormingDataCenters

This repository contains models and case studies of our article:

> Making data centers good grid citizens via converter control, 2026.

Please, we would appreciate it much if you can cite our paper when you use all or part of the work, including models and case studies, in your work.

## Installation

To reproduce the case studies, follow the same steps:

1. **Clone repository**: Clone this repository.
    ```
    $ git clone https://github.com/rkravis/GridFormingDataCenters.git
    ```
2. **Python**: Make sure you have [python3.14](https://www.python.org/downloads/release/python-3145rc1/). Create your python3.14 virtual environment:
    ```
    $ python3.14 -m venv .venv 
    $ source .venv/bin/activate
    (.venv)$ 
    ```
3. **Install sting**: Download sting (https://github.com/REAM-lab/STING) and install sting in your python3.14 virtual environment you have created in the previous step: 
     ```
    (.venv)$ cd sting
    (.venv) sting$ pip install -e . 
    ```
    Important: We have incorporated the dynamical models, we develop in this work, into sting. So when you are downloading sting, you are downloading the dynamical models that 
    are needed to run the case studies. The sting package is regularly updated with newer versions, then having your sting version updated is important to run the case studies.

4. **Install ipopt**: Install ipopt, a nonlinear solver, that is used to run an ACOPF. This step is also mentioned in the sting installation.

    Up to this step, you should be able to run the case studies. However, if you want to design the controllers that our paper proposes, you need to install aditional packages:

5. **Install cmas**: Download cmas (https://github.com/REAM-lab/cmas) and install cmas in your python3.14 virtual environment:
     ```
    (.venv)$ cd cmas
    (.venv) cmas$ pip install -e . 
    ```
6. **Install a SDP solver**: Install a semi-definite programming solver, for example, sdpt3, mosek, etc. Then adquire a licence for that solver if needed. If you opt to install mosek (https://docs.mosek.com/11.0/install/installation.html), they can give a free academic licence (https://www.mosek.com/products/academic-licenses/).



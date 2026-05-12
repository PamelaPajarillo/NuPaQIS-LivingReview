# A Living Review of Quantum Information Science in Nuclear and Particle Physics

[![DOWNLOAD_PDF](https://img.shields.io/badge/Download-PDF_Version-81b7df)](https://docs.google.com/viewer?url=https://raw.githubusercontent.com/PamelaPajarillo/NUPAQIS-LivingReview/main/NUPAQIS.pdf) [![Preprint Draft for arXiV](https://img.shields.io/badge/arXiV_Post-TBA-blue)](https://www.overleaf.com/read/wkqcjgwhfwpb#e5842a)

Authors: Pamela Pajarillo, So Chigusa, Sokratis Trifinopoulos, Jesse Thaler 
 
Number of Papers: 239 
 
*Inspired by <a href="https://iml-wg.github.io/HEPML-LivingReview/">"A Living Review of Machine Learning for High Energy Physics"</a>, the goal of this repository is to provide an extensive list of citations for those developing and applying quantum information approaches to experimental, phenomenological, or theoretical analyses.  Applications of quantum information science to high energy physics is a relatively new field of research.  This repository will be updated as often as possible with the relevant literature.  Suggestions are most welcome.*

The goal of this repository is to collect references for quantum information science as applied to particle and nuclear physics. The papers are listed in chronological order. Reviews, whitepapers, and inproceedings are listed at the beginning of each section and can be found <a href="/BY_NUPA/README.md#textbfreviews-and-whitepapers"> here </a>. 

The repository is organized in two ways: 
* [![MAIN_TO_NUPA](https://img.shields.io/badge/Link_to-Living_Review_by_Nuclear_and_Particle_Physics-5BC0EB)](/BY_NUPA#a-living-review-of-quantum-information-science-in-nuclear-and-particle-physics-organized-by-nupa-topics) NuPa topics are the main categories and QIS topics are the subcategories 
* [![MAIN_TO_NUPA](https://img.shields.io/badge/Link_to-Living_Review_by_Quantum_Information_Science-9BC53D)](/BY_QIS#a-living-review-of-quantum-information-science-in-nuclear-and-particle-physics-organized-by-qis-topics) QIS topics are the main categories and NuPa topics are the subcategories

The NuPa and QIS topics and a plot of the papers by NuPaQIS are listed below. 

##  $\textbf{\color{#5BC0EB}{Nuclear and Particle Physics (NuPa) Topics}}$

<details>
<summary> <b>Reviews, Whitepapers, and Proceedings: </b> <a href="/BY_NUPA/README.md#textbfreviews-and-whitepapers"> Link to Papers </a>  <code>Expand for Description</code> </summary>



The references below contain (static) reviews and whitepapers listed in applications of quantum information science to particle physics. Note that the majority of the references are from the Snowmass Community Planning Exercises.
</details>

<details>
<summary> <b>Anomaly Detection: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53danomaly-detection"> Link to Papers </a>  <code>Expand for Description</code> </summary>



Searching for Beyond the Standard Model (BSM) is one of the most important tasks at the Large Hadron Collider (LHC). Traditional searches at the LHC typically look for specific theoretical BSM signal(s). Hundreds of searches for new particles have been performed at the LHC, and so far, there has been no significant deviation observed from the SM. This motivates the need for more model-agnostic search strategies that can look for any data feature inconsistent with the Standard Model, regardless of the underlying BSM hypothetisis. Anomaly detection is a strategy that aims to identify events that deviate from the expected background without relying on specific signal models. Anomaly detection can be performed using machine learning techniques, which can be broadly categorized into unsupervised, weakly supervised, and semi-supervised methods. Unsupervised methods do not have any label information and learn directly from the background-dominated data. Weakly supervised methods have noisy labels, meaning that the labels are 'possibly signal-depleted' or 'possibly signal-enriched'. Semi-supervised methods have a small amount of labeled data, where signal simulations are used to build some signal sensitivity. Additionally, it has been proposed to use anomaly detection to look for BSM physics at the trigger level, which is the first stage of data processing at the LHC, and for detector monitoring to maintain high data quality. These methods will be crucial for the next generation of collider experiments, such as the High-Luminosity LHC (HL-LHC), which will produce an unprecedented amount of data. 

References:
  - The LHC Olympics 2020: A Community Challenge for Anomaly Detection in High Energy Physics: https://arxiv.org/abs/2101.08320
  - Anomaly Detection for Physics Analysis and Less than Supervised Learning: https://arxiv.org/pdf/2010.14554
  - Machine Learning for Anomaly Detection in Particle Physics: https://arxiv.org/abs/2312.14190
  - Anomaly Detection Section in HEPML-LivingReview: https://iml-wg.github.io/HEPML-LivingReview/#anomaly-detection
</details>

<details>
<summary> <b>Beyond the Standard Model: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53dbeyond-the-standard-model"> Link to Papers </a>  <code>Expand for Description</code> </summary>



The Standard Model (SM) of particle physics is a quantum field theory that describes the fundamental particles and their interactions: electromagnetic, weak, and strong forces. It has been extensively tested and confirmed through numerous experiments over the past several decades, most notably the discovery of the Higgs boson in 2012.  However, the SM fails to explain several phenomena, necessitating the proposal of Beyond the Standard Model (BSM) physics. However, the SM is not a complete theory of fundamental physics, as it does not include gravity as described by Einstein's theory of General Relativity, does not account for dark matter or dark energy, does not explain the matter-antimatter asymmetry in the universe, or the small but non-zero masses of neutrinos. BSM physics refers to theoretical frameworks that extend or modify the SM to address these shortcomings. Examples of BSM theories include supersymmetry, extra dimensions, grand unified theories, and various dark matter models. The search for BSM physics is a major focus of current and future experimental efforts in particle physics, including collider experiments like the LHC, as well as non-collider experiments such as those searching for dark matter as well as or measuring neutrino properties.

References:
  - Goldberg, Dave. The Standard Model in a Nutshell. Princeton University Press, 2017.
  - Quantum Field Theory and the Standard Model, Matthew D. Schwartz, Cambridge U. Press, 2014.
</details>

<details>
<summary> <b>Dark Matter - Particle-like Dark Matter: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53ddark-matter---particle-like-dark-matter"> Link to Papers </a>  <code>Expand for Description</code> </summary>



Dark Matter (DM) constitutes about 85\% of the matter in the universe but remains non-observable. Unlike normal matter, DM does not emit, absorb, or reflect light, making it invisible to electromagnetic observations. The existence of DM is inferred from its gravitational effects on visible matter. The nature of DM is one of the most significant open questions in physics. There are many theoretical candidates for DM, which can be broadly categorized into particle-like and wave-like candidates.
A list of particle-like dark matter candidates include: 
  (1) Weakly Interacting Massive Particles (WIMPs):
  (2) Light Dark Matter:
  (3) Millicharged Particles: 
  (4) Dark Photons (massive):
  (5) Sterile Neutrinos:


References:
  - A Primer on Dark Matter: https://arxiv.org/abs/2411.05062
  - Dark Matter Review: https://arxiv.org/abs/2406.01705
</details>

<details>
<summary> <b>Dark Matter - Wave-like Dark Matter: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53ddark-matter---wave-like-dark-matter"> Link to Papers </a>  <code>Expand for Description</code> </summary>



Dark Matter (DM) constitutes about 85\% of the matter in the universe but remains non-observable. Unlike normal matter, DM does not emit, absorb, or reflect light, making it invisible to electromagnetic observations. The existence of DM is inferred from its gravitational effects on visible matter. The nature of DM is one of the most significant open questions in physics. There are many theoretical candidates for DM, which can be broadly categorized into particle-like and wave-like candidates.
A list of wave-like dark matter candidates include: 
  (1) Axions and Axion-like Particles (ALPs): An axion is a hypothetical particle theorized to solve the strong CP problem in quantum chromodynamics (QCD) and the cosmological matter-antimatter asymmetry.
  (2) Ultralight Dark Matter: 
  (3) Fuzzy Dark Matter:
  (4) Dark Photons (ultralight):
  (5) Primordial Black Holes: 
  (6) Q-balls:
  (7) Compact Composite Objects: 

  References:
  - A Primer on Dark Matter: https://arxiv.org/abs/2411.05062
  - Dark Matter Review: https://arxiv.org/abs/2406.01705
  - Axion Dark Matter: What is it and Why Now? https://arxiv.org/abs/2105.01406
  - PDG Review on Axions and Axion-like Particles https://pdg.lbl.gov/2024/reviews/rpp2024-rev-axions.pdf
</details>

<details>
<summary> <b>Detector Technologies and Simulations: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53ddetector-technologies-and-simulations"> Link to Papers </a>  <code>Expand for Description</code> </summary>



To be written

References:
  - TBA
</details>

<details>
<summary> <b>Effective Field Theories: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53deffective-field-theories"> Link to Papers </a>  <code>Expand for Description</code> </summary>



To be written

References:
  - TBA
</details>

<details>
<summary> <b>Event Classification: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53devent-classification"> Link to Papers </a>  <code>Expand for Description</code> </summary>



An event is the outcome of a collision between two incoming particles, or the outcome of an isolated decay of a particle, which consists of a number of outgoing particles. Event classification is the task of distinguishing the signal events of interest from background events.  
References:
  - TBA
</details>

<details>
<summary> <b>Event Generation: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53devent-generation"> Link to Papers </a>  <code>Expand for Description</code> </summary>



In high energy particle physics, an event is defined as the outcome of a collision between two incoming particles, or the outcome of an isolated decay of a particle, which consists of a number of outgoing particles. An event generator is a numerical algorithm that produces random sequences of simulated events. The aim of an event generator is to predict all observable properties of a collision or a decay process. An event generator is an important tool for interpreting collider data because it gives predictions for what an event would look like before interacting with detectors, and is essential to linking theories with experiments. An event generator is a numerical algorithm that produces random simulated events sampled according to the probability distributions predicted by the underlying quantum theory.     The aim of an event generator is to predict all observable properties of a collision or decay, given a Lagrangian and the kinematics of the initial state, by carrying out the full chain: matrix-element computation for the hard process, parton-shower evolution from high to low momentum scales, hadronization of the resulting partons into observable hadrons, and decays of unstable particles. Standard tools include PYTHIA, HERWIG, SHERPA, and MADGRAPH; the calculations require very-high-dimensional phase-space integration carried out via Monte Carlo methods.

References:
  - Herwig++ Physics and Manual: https://arxiv.org/abs/0803.0883
  - A comprehensive guide to the physics and usage of PYTHIA 8.3: https://arxiv.org/abs/2203.11601
</details>

<details>
<summary> <b>Astrophysics and Cosmology: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53dastrophysics-and-cosmology"> Link to Papers </a>  <code>Expand for Description</code> </summary>



To be written

References:
  - Astrophysics and Cosmology: https://cds.cern.ch/record/435281/files/p109.pdf
</details>

<details>
<summary> <b>Jet Reconstruction: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53djet-reconstruction"> Link to Papers </a>  <code>Expand for Description</code> </summary>



In high-energy particle collisions, jets are a collection of collimated hadrons and other particles produced by the hadronization of quarks and gluons. Since quarks and gluons carry color charge, they cannot exist as free particles due to QCD confinement. Instead, they fragment and hadronize, resulting in a spray of energetic hadrons, which we define as jets. Jet reconstruction is the procedure used to group these final-state particles into composite objects, and by measuring their direction and energy, we can infer the properties of the original partons. Jet reconstruction is typically done using clustering algorithms such as anti-\(k_T\), \(k_T\), or Cambridge/Aachen. Reconstructed jets are fundamental observables in collider physics, used to probe QCD, identify heavy-flavor decays, and search for physics beyond the Standard Model. The study of jets and their properties is crucial for understanding the underlying physics processes in high-energy collisions.
References:
  - Towards Jetography: https://arxiv.org/pdf/0906.1833
  - Exploring jets: substructure and flavour tagging in CMS and ATLAS: https://arxiv.org/abs/2410.14330
</details>

<details>
<summary> <b>Lattice Scalar/Fermion Theories: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53dlattice-scalar/fermion-theories"> Link to Papers </a>  <code>Expand for Description</code> </summary>



To be written

References:
  - TBA
</details>

<details>
<summary> <b>Lattice Gauge Theories: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53dlattice-gauge-theories"> Link to Papers </a>  <code>Expand for Description</code> </summary>



To be written

References:
  - TBA
  
</details>

<details>
<summary> <b>Quantum Chromodynamics: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53dquantum-chromodynamics"> Link to Papers </a>  <code>Expand for Description</code> </summary>



Quantum Chromodynamics (QCD), a non-Abelian gauge theory with symmetry group $SU(3)$, is the theory of strong interaction between quarks and gluons and how they bind together to form hadrons. The QCD Lagrangian is given by $\mathcal{L}_{\text{QCD}} = -\frac{1}{4} F_{\mu\nu}^a F^{a\mu\nu} + \sum_{f=1}^{N_f} \bar{\psi}_f (i\gamma^\mu D_\mu - m_f) \psi_f$, where $F_{\mu\nu}^a$ is the gluon field strength tensor, $\psi_f$ are the quark fields for each flavor $f$, $m_f$ are the quark masses, and $D_\mu$ is the covariant derivative. QCD is a fundamental part of the Standard Model of particle physics. QCD has two key energy regimes: at high energies, asymptotic freedom allows for perturbative calculations, while at low energies, color confinement means that quarks and gluons are not observed individually but are confined with color-neutral hadrons. QCD also exhibits chiral symmetry breaking, which is responsible for the generation of hadron masses and the existence of pseudo-Goldstone bosons (pions). 

References:
  - R. K. Ellis, W. J. Stirling, and B. R. Webber, *QCD and Collider Physics*, Cambridge University Press, 1996.
  
</details>

<details>
<summary> <b>Quantum Correlations at Colliders: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53dquantum-correlations-at-colliders"> Link to Papers </a>  <code>Expand for Description</code> </summary>



To be written

References:
  - Quantum entanglement and Bell inequality violation at colliders: https://arxiv.org/abs/2402.07972
</details>

<details>
<summary> <b>Schwinger Model: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53dschwinger-model"> Link to Papers </a>  <code>Expand for Description</code> </summary>



Developed by Julian Schwinger in 1962, the Schwinger model is a 1+1 dimensional quantum field theory that describes quantum electrodynamics (QED), the theory of light (photons) interacting with charged particles (electrons and positrons). The Lagrangian of the Schwinger model is given by $\mathcal{L} = \bar{\psi}(i\gamma^{\mu}D_{\mu} - m)\psi -\frac{1}{4} F_{\mu\nu}F^{\mu\nu}$ where $F_{\mu\nu}$ is the electromagnetic field strength tensor, $\psi$ is the Dirac fermion field representing electrons and positrons, $m$ is the mass of the fermions, and $D_{\mu} = \partial_{\mu} + ie A_{\mu}$ is the gauge covariant derivative. The Schwinger model has properties that are directly analogous to features in quantum chromodynamics (QCD)
References:
  - Supplemetary Lecture 21 - Bosonization in 1+1 Dimensions and Solving the Schwinger Model: https://relativitydoctor.com/wp-content/uploads/2021/08/Supplemental-Lecture-21-Part-VIII-Bosonization-in-11-Dimensions-and-Solving-the-Schwinger-Model-Introduction-to-the-Foundations-of-Quantum-Field-Theory-for-Physics-Students.pdf
  - David Tong's Lectures on Gauge Theory, Chapter 7: https://www.damtp.cam.ac.uk/user/tong/gaugetheory.html
  - Charge shielding and quark confinement in the Schwinger model: https://doi.org/10.1016/0003-4916(75)90212-2
  - Gauge Invariance and Mass. II: https://journals.aps.org/pr/abstract/10.1103/PhysRev.128.2425
  - Selected Topics in Gauge Theories, Chapter 5: https://link.springer.com/book/10.1007/3-540-16064-7
</details>

<details>
<summary> <b>Track Reconstruction: </b> <a href="/BY_NUPA/README.md#textbfcolor9bc53dtrack-reconstruction"> Link to Papers </a>  <code>Expand for Description</code> </summary>



To be written

References:
  - Track reconstruction as a service for collider physics: https://arxiv.org/abs/2501.05520
  
</details>



##  $\textbf{\color{#9BC53D}{Quantum Information Science (QIS) Topics}}$

<details>
<summary> <b>Reviews, Whitepapers, and Proceedings: </b> <a href="/BY_QIS/README.md#textbfreviews-and-whitepapers"> Link to Papers </a>  <code>Expand for Description</code> </summary>



The references below contain (static) reviews and whitepapers listed in applications of quantum information science to particle physics. Note that the majority of the references are from the Snowmass Community Planning Exercises.
</details>

<details>
<summary> <b>Continuous Variable Quantum Computing: </b> <a href="/BY_QIS/README.md#textbfcolor5bc0ebcontinuous-variable-quantum-computing"> Link to Papers </a>  <code>Expand for Description</code> </summary>



In constrast to the more commonly used discrete variable quantum computing, which uses a finite number of qubits as the basic unit of information, continuous variable quantum computing is a quantum computing paradigm that uses a large number of harmonic oscillator modes, which can be represented as $\ket{\psi} = \int \,dx\, \psi(x) \ket{x} $, where $\ket{x}$ is the eigenstate of the position operator. 

References:
  - Quantum computation over continuous variables: https://arxiv.org/abs/quant-ph/9810082
  - Quantum information with continuous variables: https://arxiv.org/abs/quant-ph/0410100
</details>

<details>
<summary> <b>Quantum Algorithms - Grover's Search Algorithm: </b> <a href="/BY_QIS/README.md#textbfcolor5bc0ebquantum-algorithms---grover's-search-algorithm"> Link to Papers </a>  <code>Expand for Description</code> </summary>



The quantum search algorithm, also known as Grover's algorithm, performs a generic search for a solution to a search problem. Assuming that the solutions of the search problem can be expressed as binary strings of length $n$, such that $N= 2^n$, where $N$ is the dimension of the search space, then any search problem can be represented as a function $f(x)$ where $f(x) = 1$ if $x$ is a solution and $f(x) = 0$ otherwise. Grover's algorithm aims to find an input $x \in \{0,1\}^n$ such that $f(x) = 1$. Suppose the function $f$ is implemented by an oracle, a black box that can recognize solutions to the search problem. Classically, it would take $\mathcal{O}(N)$ queries to the oracle to find the solution, however, using Grover's algorithm would allow this search to be sped up substantially, requiring only $\mathcal{O}(\sqrt{N})$ queries. The quantum oracle can be represented by a unitary operator $O$, defined by its action: $\ket{x} \longmapsto (-1)^{f(x)} \ket{x}$. Therefore, the oracle marks the solution to the search problem by a phase shift. The algorithm starts with the computer with the state $\ket{0}^{\otimes n}$ and acting the Hadamard gates on all $n$ qubits gives us the state $\ket{\psi} = \frac{1}{\sqrt{N}} \sum_{x=0}^{N-1}\ket{x}$. Grover's algorithm consists of repeated applications of a quantum subroutine called Grover iteration which are as follows: (1) Apply the oracle $O$; (2) Apply $H^{\otimes n}$; (3) Perform a conditional phase shift: $\ket{x} \rightarrow -(-1)^{\delta_{x0}}\ket{x}$. (4) Apply $H^{\otimes n}$. This Grover iteration is repeated $\mathcal{O}(\sqrt{N})$ times. This can be extended to a search problem with $M$ solutions, with $1 \leq M \leq N$, and the Grover iteration can be applied $\mathcal{O}(\sqrt{N/M})$ times to get the solutions. 

References:
  - Nielsen, Michael A., and Isaac L. Chuang. *Quantum Computation and Quantum Information*. 10th anniversary ed. [or 2nd ed.], Cambridge University Press, 2010.
  - Kaye, Phillip., Raymond Laflamme, and Michele Mosca. An Introduction to Quantum Computing. Oxford University Press, 2007.
</details>

<details>
<summary> <b>Quantum Algorithms - Harrow-Hassadim-Lloyd Algorithm: </b> <a href="/BY_QIS/README.md#textbfcolor5bc0ebquantum-algorithms---harrow-hassadim-lloyd-algorithm"> Link to Papers </a>  <code>Expand for Description</code> </summary>



The Harrow-Hassadim-Lloyd (HHL) algorithm is a quantum algorithm for solving systems of linear equations. Given an $N \times N$ Hermitian matrix $A$ and a unit vector $\vec{b}$, the HHL algorithm aims to find the solution $\vec{x}$ such that $A \vec{x} = \vec{b}$. The algorithm consists of five main steps: (1) State Preparation: Prepare the state $\ket{\vec{b}}$; (2) Quantum Phase Estimation (QPE): This step estimates the eigenvalues of the matrix $A$ by applying QPE to the unitary operator $e^{iAt}$, where $t$ is a chosen time parameter. This step requires the ability to efficiently implement the Hamiltonian simulation of $A$. (3) Controlled Rotation and Measurement of the Ancilla Qubit: After obtaining the eigenvalues from QPE, controlled rotations are applied to an ancillary qubit based on the inverse of the eigenvalues. This step effectively encodes the solution vector into the amplitudes of the quantum state. (4) Inverse QPE: Finally, the QPE process is reversed to disentangle the ancillary qubits from the system, leaving behind a quantum state that approximates the solution vector $\vec{x}$. (5) Measurement: The final step involves measuring the quantum state to extract information about the solution vector $\vec{x}$. The HHL algorithm provides an exponential speedup over classical algorithms for solving linear systems under certain conditions, such as when $A$ is sparse and well-conditioned. 

References:
  - Harrow, Aram W., Avinatan Hassidim, and Seth Lloyd. "Quantum algorithm for linear systems of equations": https://doi.org/10.1103/PhysRevLett.103.150502 
  - Zaman, Anika, Hector Jose Morrell, and Hiu Yung Wong. "A step-by-step HHL algorithm walkthrough to enhance understanding of critical quantum computing concepts.": https://ieeexplore.ieee.org/document/10189828
</details>

<details>
<summary> <b>Quantum Algorithms - Quantum Simulations: </b> <a href="/BY_QIS/README.md#textbfcolor5bc0ebquantum-algorithms---quantum-simulations"> Link to Papers </a>  <code>Expand for Description</code> </summary>



Richard Feynman first proposed the idea of quantum simulation in 1982, where he noted that simulating quantum systems on a classical computer was hard because the number of resources required grows exponentially with the size of the system, and suggested that quantum systems could be efficiently simulated by other quantum systems. Let us consider a general quantum simulation problem: finding the state of a quantum system described by a wavefunction $\ket{\psi}$ at some time $t$. Focusing on the case of time-independent Hamiltonian and assuming $\hbar = 1$, the solution of the Schrödinger equation $\frac{d}{dt}\ket{\psi} = -iH\ket{\psi}$ is given by $\ket{\psi(t)} = e^{-iHt} \ket{\psi(0)}$, where $H$ is the Hamiltonian of the system. The goal is to solve for $\ket{\psi(t)}$ given the initial state $\ket{\psi(0)}$ and the Hamiltonian $H$. Seth Lloyd later showed that Feynman's idea of quantum simulation could be implemented on a quantum computer. For each degree of freedom of the system, we can allocate a quantum register containing a sufficient number of qubits to approximate the state of that degree of freedom to some desired accuracy. We can then write the Hamiltonian of the system as $H = \sum_{l=1}^m H_l$, where each $H_l$ operates on only a few degrees of freedom. The Trotter decomposition can be used to approximate the time evolution operator as $e^{-iHt} = \left( e^{-iH_1 \Delta t} e^{-iH_2 \Delta t} \cdots e^{-iH_m \Delta t} \right) - \frac{1}{2}\sum_{jk}[H_j, H_k]\Delta t^2 + \mathcal{O}(t^3)$. Each $e^{-iH_l \Delta t}$ can be simulated using quantum gates on the qubits in the register corresponding to the degrees of freedom that $H_l$ operates on. To simulate the time evolution of the system for a total time $t$, we can repeat this process $t = n \Delta t$ times, giving us $e^{-iHt} = (e^{-iH\Delta t})^n = \left( \prod_l e^{-iH_l \Delta t} \right)^n - \frac{n}{2}\sum_{jk}[H_j, H_k]\Delta t^2 + \mathcal{O}(t^3)$. The quantum simulation takes $O(mn) steps, and reproduces the original time evolution to an accuracy of $h^2 t^2 m^2 / n$, where $h$ is the average size of $\lVert[H_j, H_k]\rVert$. This approach allows us to simulate quantum systems that are intractable for classical computers, such as many-body quantum systems, quantum chemistry problems, and high-energy physics phenomena.

References:
  - Nielsen, Michael A., and Isaac L. Chuang. *Quantum Computation and Quantum Information*. 10th anniversary ed. [or 2nd ed.], Cambridge University Press, 2010.
  - Quantum Simulation: https://arxiv.org/pdf/1308.6253
  - Lloyd, Seth. "Universal quantum simulators": https://www.science.org/doi/epdf/10.1126/science.273.5278.1073
</details>

<details>
<summary> <b>Quantum Algorithms - Quantum Walks: </b> <a href="/BY_QIS/README.md#textbfcolor5bc0ebquantum-algorithms---quantum-walks"> Link to Papers </a>  <code>Expand for Description</code> </summary>



A random walk is a random process that describes a path that consists of a sequence of steps that are determined randomly. An example of a one dimensional discrete random walk is a random walk on the integer number line starting at $0$, and each step moves $+1$ or $-1$ with an equal probability, which is analogous to flipping a coin then, depending on the outcome, move forward or backwards on the number line. This can be described as a Markov chain, a sequence of random variables with the property that the probability of moving to the next step only depends on the current step and not the previous step, i.e. $p(X_{n+1} = x | X_1 = x_1, X_2 = x_2, \ldots) = p(X_{n+1} = x | X_n = x_n)$. This can be extended to higher dimensions. An example of a continuous random walk is Brownian motion, the random motion of particles in a medium. The quantum discrete random walk defines the movement of a walker in position basis, $\mathcal{H}_P = \{ \ket{i} : i \in \mathbb{Z} \}$, controlled by the coin in the spin-$\frac{1}{2}$ basis, $\mathcal{H}_C = \{\ket{\uparrow}, \ket{\downarrow}\}$. The translation of the walker can be represented by the unitary operator $T = \sum \ket{i + 1} \bra{i} \otimes \ket{\uparrow} \bra{\uparrow} + \sum \ket{i-1} \bra{k} \otimes \ket{\downarrow} \bra{\downarrow} $, where the index $i$ runs over $\mathcal{Z}$. Therefore, $T \ket{i} \ket{\uparrow} = \ket{i + 1} \ket{\uparrow}$ and $T \ket{i} \ket{\downarrow} = \ket{i-1} \ket{\downarrow}$. A single step of the random walk is constructed from a coin flip unitary operation $C$ and the translation operator, $T$. Therefore, a single step can be represented as a unitary operator $U = T \cdot (C \otimes \mathbb{I})$. An $N$-step quantum walk is defined by $U^N$. In the quantum random walk, the coin register is not measured during each step. This introduces interference, which is drastically different from the classical random walk.

References:
  - Quantum Random Walks - A Comprehensive Review: https://arxiv.org/abs/1201.4780
</details>

<details>
<summary> <b>Quantum Annealing: </b> <a href="/BY_QIS/README.md#textbfcolor5bc0ebquantum-annealing"> Link to Papers </a>  <code>Expand for Description</code> </summary>



Quantum annealing is a quantum computing method used to solve optimization problems. It is currently the only quantum computing paradigm that enables architectures with large number of qubits, such as D-Wave Systems' Pegasus quantum processor chip with 5000 qubits. Quantum annealers solve very specific optimization problems called Quadratic Unconstrained Binary Optimization (QUBO) problems. The QUBO problem consists of finding a binary string that is minimal with respect to a quadratic polynomial over binary variables. The main challenge is to rephrase the loss function to a QUBO problem, which is equivalent to finding the ground state of a corresponding Ising model, whose Hamiltonian is given by $H(\sigma) = \sum_{i,j=1}^{n}J_{ij} s_i s_j + \sum_{i=1}^{n} h_i s_i$ where $s_i \in \{-1, +1\}$ are the spin values, and $h_i$ and $J_{ij}$ are adjustable constants that represents biases and coupling strengths, respectively. The Hamiltonian of the quantum version of the Ising model, the transverse field Ising model, is given by $ H_f = \sum_{i,j = 1}^{n}J_{ij}\sigma_{i}^{z}\sigma_{j}^{z} + \sum_{i}^{n}h_i\sigma_{i}^{z}$ where $\sigma_{i}^{z}$ is the Pauli-$Z$ acting on qubit $i$. In quantum annealing, one initializes the system in the ground state of the initial Hamiltonian $H_i$, given by $H_i = \sum_{i=1}^{n}\sigma_{i}^{x} $ corresponding to the state $(\ket{0} + \ket{1})^{\otimes n}$. The quantum adiabatic theorem states that if the transition between two Hamiltonians is gradual, the system will stay in the ground state. After initializing the system, it slowly evolves by changing the Hamiltonian given by $H(t) = \left(1 - \frac{t}{T}\right)H_i + \frac{t}{T} H_f $ where $T$ is the total time in the annealing process. Measuring the final state after the anneal will give the solution to the QUBO problem, since the final system is in an eigenstate of $H_f$. 

References:
  - D-Wave Documentation: https://docs.dwavequantum.com/en/latest/quantum_research/quantum_annealing_intro.html
  - Quantum Annealing and Analog Quantum Computation: https://arxiv.org/abs/0801.2193
</details>

<details>
<summary> <b>Quantum Entanglement and Bell Inequalities: </b> <a href="/BY_QIS/README.md#textbfcolor5bc0ebquantum-entanglement-and-bell-inequalities"> Link to Papers </a>  <code>Expand for Description</code> </summary>



One of the main features of quantum information processing is quantum entanglement. A quantum state $\ket{\psi}$ is said to be entangled if it cannot be written as a product of individual states of the subsystems. 

References: 
  - Nielsen, Michael A., and Isaac L. Chuang. *Quantum Computation and Quantum Information*. 10th anniversary ed. [or 2nd ed.], Cambridge University Press, 2010.
</details>

<details>
<summary> <b>Quantum Machine Learning - Supervised Methods: </b> <a href="/BY_QIS/README.md#textbfcolor5bc0ebquantum-machine-learning---supervised-methods"> Link to Papers </a>  <code>Expand for Description</code> </summary>



To be written

References:
  - Quantum machine learning on near-term quantum devices: Current state of supervised and unsupervised techniques for real-world applications: https://doi.org/10.1103/PhysRevApplied.21.067001
  - Quantum Machine Learning: https://arxiv.org/abs/1611.09347
</details>

<details>
<summary> <b>Quantum Machine Learning - Unsupervised Methods: </b> <a href="/BY_QIS/README.md#textbfcolor5bc0ebquantum-machine-learning---unsupervised-methods"> Link to Papers </a>  <code>Expand for Description</code> </summary>



To be written

References:
  - Quantum machine learning on near-term quantum devices: Current state of supervised and unsupervised techniques for real-world applications: https://doi.org/10.1103/PhysRevApplied.21.067001
  - Quantum Machine Learning: https://arxiv.org/abs/1611.09347
</details>

<details>
<summary> <b>Quantum Machine Learning - Variational Quantum Algorithms: </b> <a href="/BY_QIS/README.md#textbfcolor5bc0ebquantum-machine-learning---variational-quantum-algorithms"> Link to Papers </a>  <code>Expand for Description</code> </summary>



Variational Quantum Algorithms (VQAs) are hybrid quantum-classical algorithms that find approximate solutions to optimization problems. VQAs starts with a parameterized quantum circuit (PQC) where the parameters are optimized by a classical optimizer to minimize (or maximize) a cost function. 

References:
  - Quantum machine learning on near-term quantum devices: Current state of supervised and unsupervised techniques for real-world applications: https://doi.org/10.1103/PhysRevApplied.21.067001
  - Quantum Machine Learning: https://arxiv.org/abs/1611.09347
</details>

<details>
<summary> <b>Quantum Sensors - Atomic/Molecular/Nuclear Sensors: </b> <a href="/BY_QIS/README.md#textbfcolor5bc0ebquantum-sensors---atomic/molecular/nuclear-sensors"> Link to Papers </a>  <code>Expand for Description</code> </summary>



A list of atomic sensors include:
  (1) Atomic clocks
  (2) Atom interferometers
  (3) Atomic ensembles
  (4) Rydberg atoms
  (5) Trapped ions
  (6) Penning traps

A list of molecular sensors include:
  (1) Molecular clocks
  (2) Trapped molecules 

A list of nuclear sensors include:
  (1) Nuclear clocks
  (2) Nuclear spin ensembles


References:
  - Quantum Sensing: https://arxiv.org/abs/1611.02427
</details>

<details>
<summary> <b>Quantum Sensors - Optical/Photonic Sensors: </b> <a href="/BY_QIS/README.md#textbfcolor5bc0ebquantum-sensors---optical/photonic-sensors"> Link to Papers </a>  <code>Expand for Description</code> </summary>



A list of optical/photonic sensors include:
  (1) Superconducting qubits measuring electomagnetic fields
  (2) Optical cavities
  (3) Superconducting radio frequency cavities
  (4) Squeezed-light interferometers


References:
  - Quantum Sensing: https://arxiv.org/abs/1611.02427
</details>

<details>
<summary> <b>Quantum Sensors - Optomechanical Sensors: </b> <a href="/BY_QIS/README.md#textbfcolor5bc0ebquantum-sensors---optomechanical-sensors"> Link to Papers </a>  <code>Expand for Description</code> </summary>



A list of optical/photonic sensors include:
  (1) Mechanical sensors
  (2) Levitated sensors


References:
  - Quantum Sensing: https://arxiv.org/abs/1611.02427
</details>

<details>
<summary> <b>Quantum Sensors - Solid State Sensors: </b> <a href="/BY_QIS/README.md#textbfcolor5bc0ebquantum-sensors---solid-state-sensors"> Link to Papers </a>  <code>Expand for Description</code> </summary>



Solid state sensors measures quantum excitations in the solid material itself
A list of solid state sensors include:
  (1) Nitrogen-vacancy centers
  (2) Quantum dots
  (3) Superconducting Quantum Interference Devices (SQUIDs)
  (4) Superconducting qubits measuring quantum excitations


References:
  - Quantum Sensing: https://arxiv.org/abs/1611.02427
</details>



## Number of Papers in NuPaQIS

![NUPAQIS_Heatmap](NUPAQIS_2D_Heatmap.png)

![NUPA_Histogram](NUPA_Histogram.png)

![NUPA_Histogram](QIS_Histogram.png)


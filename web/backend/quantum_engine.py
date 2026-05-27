import numpy as np
from scipy.special import erf,gamma
from scipy.integrate import quad
from scipy.linalg import eigh,eigh_tridiagonal
from typing import Tuple,Dict,List
import warnings
warnings.filterwarnings('ignore')

class GaussianBasisFunction:
    """Gaussian basis function implementation"""
    def __init__(self,center:np.ndarray,exponent:float,l:int=0,m:int=0,n:int=0):
        self.center=center
        self.exponent=exponent
        self.l,self.m,self.n=l,m,n
        self.norm=self._compute_normalization()
    
    def _compute_normalization(self)->float:
        """Compute normalization constant for Gaussian basis function"""
        factor=(2*self.exponent/np.pi)**0.75
        l_fact,m_fact,n_fact=1,1,1
        if self.l>0:l_fact=np.prod([2*i-1 for i in range(1,self.l+1)])
        if self.m>0:m_fact=np.prod([2*i-1 for i in range(1,self.m+1)])
        if self.n>0:n_fact=np.prod([2*i-1 for i in range(1,self.n+1)])
        denom=np.sqrt(l_fact*m_fact*n_fact)
        return float(factor/denom)
    
    def evaluate(self,r:np.ndarray)->float:
        """Evaluate basis function at position r"""
        dr=r-self.center
        dist_sq=np.sum(dr**2)
        exp_part=np.exp(-self.exponent*dist_sq)
        x_part=dr[0]**self.l if self.l>0 else 1.0
        y_part=dr[1]**self.m if self.m>0 else 1.0
        z_part=dr[2]**self.n if self.n>0 else 1.0
        return float(self.norm*x_part*y_part*z_part*exp_part)

class QuantumComputationEngine:
    """Quantum computation engine implementing HF and DFT methods"""
    
    def __init__(self,geometry:np.ndarray,nuclear_charges:np.ndarray,basis_functions:List[GaussianBasisFunction]):
        """
        Initialize quantum engine
        geometry: Nx3 array of atomic positions
        nuclear_charges: N array of nuclear charges
        basis_functions: List of GaussianBasisFunction objects
        """
        self.geometry=geometry
        self.nuclear_charges=nuclear_charges
        self.basis=basis_functions
        self.nbasis=len(basis_functions)
        self.converged=False
        self.iteration_history=[]
    
    def compute_overlap_matrix(self)->np.ndarray:
        """Compute overlap matrix S_ij"""
        S=np.zeros((self.nbasis,self.nbasis))
        for i in range(self.nbasis):
            for j in range(i,self.nbasis):
                S[i,j]=self._overlap_integral(i,j)
                if i!=j:S[j,i]=S[i,j]
        return S
    
    def _overlap_integral(self,i:int,j:int)->float:
        """Compute overlap integral between basis functions i and j"""
        gi,gj=self.basis[i],self.basis[j]
        a,b=gi.exponent,gj.exponent
        Ra,Rb=gi.center,gj.center
        Rp=(a*Ra+b*Rb)/(a+b)
        rab_sq=np.sum((Ra-Rb)**2)
        exp_part=np.exp(-a*b*rab_sq/(a+b))
        prefactor=(np.pi/(a+b))**1.5*gi.norm*gj.norm
        
        # Compute angular part (simplified for s-type orbitals)
        angular=1.0
        for l_i,l_j in zip([gi.l,gi.m,gi.n],[gj.l,gj.m,gj.n]):
            if l_i==0 and l_j==0:continue
            elif l_i==0 or l_j==0:angular*=0.5
        
        return float(prefactor*angular*exp_part)
    
    def compute_kinetic_matrix(self)->np.ndarray:
        """Compute kinetic energy matrix T_ij"""
        T=np.zeros((self.nbasis,self.nbasis))
        for i in range(self.nbasis):
            for j in range(i,self.nbasis):
                T[i,j]=self._kinetic_integral(i,j)
                if i!=j:T[j,i]=T[i,j]
        return T
    
    def _kinetic_integral(self,i:int,j:int)->float:
        """Compute kinetic energy integral"""
        gi,gj=self.basis[i],self.basis[j]
        a,b=gi.exponent,gj.exponent
        Ra,Rb=gi.center,gj.center
        rab_sq=np.sum((Ra-Rb)**2)
        
        # Simplified kinetic integral
        overlap=self._overlap_integral(i,j)
        term1=b*(2*(1+2*b)+1)*overlap
        term2=-2*b**2*overlap
        term3=-0.5*rab_sq*overlap
        
        return float(term1+term2+term3)
    
    def compute_nuclear_attraction_matrix(self)->np.ndarray:
        """Compute nuclear attraction matrix V_ij"""
        V=np.zeros((self.nbasis,self.nbasis))
        for i in range(self.nbasis):
            for j in range(i,self.nbasis):
                V[i,j]=self._nuclear_attraction(i,j)
                if i!=j:V[j,i]=V[i,j]
        return V
    
    def _nuclear_attraction(self,i:int,j:int)->float:
        """Compute nuclear attraction integral"""
        integral=0.0
        gi,gj=self.basis[i],self.basis[j]
        a,b=gi.exponent,gj.exponent
        Ra,Rb=gi.center,gj.center
        Rp=(a*Ra+b*Rb)/(a+b)
        
        for k,Zk in enumerate(self.nuclear_charges):
            Rk=self.geometry[k]
            Rpk_sq=np.sum((Rp-Rk)**2)
            rab_sq=np.sum((Ra-Rb)**2)
            exp_part=np.exp(-a*b*rab_sq/(a+b))
            T=float(a*b*Rpk_sq/(a+b))
            
            # Boys function approximation
            boys_val=self._boys_function(0,T)
            prefactor=2*np.pi/(a+b)*gi.norm*gj.norm*exp_part*boys_val
            integral-=Zk*prefactor
        
        return float(integral)
    
    def _boys_function(self,n:int,T:float)->float:
        """Compute Boys function F_n(T)"""
        if T<1e-12:
            return float(1.0/(2*n+1))
        sqrt_T=np.sqrt(T)
        if n==0:
            return float(0.5*np.sqrt(np.pi/T)*erf(sqrt_T))
        else:
            return float(((2*n-1)*self._boys_function(n-1,T)-np.exp(-T))/(2*T))
    
    def compute_electron_repulsion_tensor(self)->np.ndarray:
        """Compute electron repulsion integrals (ij|kl)"""
        n=self.nbasis
        eri=np.zeros((n,n,n,n))
        for i in range(n):
            for j in range(i+1):
                for k in range(n):
                    for l in range(k+1):
                        eri[i,j,k,l]=self._eri_integral(i,j,k,l)
                        eri[i,j,l,k]=eri[i,j,k,l]
                        eri[j,i,k,l]=eri[i,j,k,l]
                        eri[j,i,l,k]=eri[i,j,k,l]
        return eri
    
    def _eri_integral(self,i:int,j:int,k:int,l:int)->float:
        """Compute electron repulsion integral (ij|kl)"""
        gi,gj,gk,gl=self.basis[i],self.basis[j],self.basis[k],self.basis[l]
        a,b,c,d=gi.exponent,gj.exponent,gk.exponent,gl.exponent
        Ra,Rb,Rc,Rd=gi.center,gj.center,gk.center,gl.center
        
        # Gaussian product centers
        Rp=(a*Ra+b*Rb)/(a+b)
        Rq=(c*Rc+d*Rd)/(c+d)
        
        rab_sq=np.sum((Ra-Rb)**2)
        rcd_sq=np.sum((Rc-Rd)**2)
        rpq_sq=np.sum((Rp-Rq)**2)
        
        eta=a*b/(a+b)
        xi=c*d/(c+d)
        
        exp_part=np.exp(-eta*rab_sq-xi*rcd_sq)
        T=float(eta*xi*rpq_sq/(eta+xi))
        
        boys_val=self._boys_function(0,T)
        prefactor=2*np.pi**2.5/(a+b)/(c+d)/np.sqrt(a+b+c+d)
        prefactor*=boys_val*gi.norm*gj.norm*gk.norm*gl.norm*exp_part
        
        return float(prefactor)
    
    def scf_iteration(self,C:np.ndarray,n_electrons:int,max_iter:int=50,threshold:float=1e-6)->Tuple[np.ndarray,float]:
        """
        Perform SCF iteration (Hartree-Fock)
        C: Initial orbital coefficients
        n_electrons: Number of electrons
        """
        S=self.compute_overlap_matrix()
        T=self.compute_kinetic_matrix()
        V=self.compute_nuclear_attraction_matrix()
        H_core=T+V
        
        try:
            S_inv_sqrt=np.linalg.inv(np.linalg.cholesky(S))
        except:
            evals,evecs=np.linalg.eigh(S)
            S_inv_sqrt=evecs@np.diag(1.0/np.sqrt(np.maximum(evals,1e-10)))@evecs.T
        
        eri=self.compute_electron_repulsion_tensor()
        n_occ=n_electrons//2
        
        energy_hist=[]
        for iteration in range(max_iter):
            # Build density matrix
            C_occ=C[:,:n_occ]
            P=2*C_occ@C_occ.T
            
            # Build Fock matrix
            F=H_core.copy()
            for i in range(self.nbasis):
                for j in range(self.nbasis):
                    for k in range(self.nbasis):
                        for l in range(self.nbasis):
                            F[i,j]+=P[k,l]*(eri[i,k,j,l]-0.5*eri[i,l,j,k])
            
            # Transform and diagonalize
            F_ortho=S_inv_sqrt.T@F@S_inv_sqrt
            evals,evecs_ortho=np.linalg.eigh(F_ortho)
            C_new=S_inv_sqrt@evecs_ortho
            
            # Compute energy
            energy=0.5*np.trace(P@(H_core+F))
            energy_hist.append(energy)
            self.iteration_history.append({'iteration':iteration+1,'energy':energy})
            
            # Check convergence
            if iteration>0 and abs(energy_hist[-1]-energy_hist[-2])<threshold:
                self.converged=True
                return C_new,energy
            
            C=C_new
        
        return C,energy_hist[-1]
    
    def dft_iteration(self,C:np.ndarray,n_electrons:int,functional:str='LDA',max_iter:int=50)->Tuple[np.ndarray,float]:
        """Perform DFT SCF iteration"""
        S=self.compute_overlap_matrix()
        T=self.compute_kinetic_matrix()
        V=self.compute_nuclear_attraction_matrix()
        H_core=T+V
        
        S_inv_sqrt=np.linalg.inv(np.linalg.cholesky(S))
        
        n_occ=n_electrons//2
        energy_hist=[]
        
        for iteration in range(max_iter):
            C_occ=C[:,:n_occ]
            P=2*C_occ@C_occ.T
            
            # DFT potential (simplified LDA)
            V_xc=self._compute_xc_potential(P,functional)
            
            # Build Kohn-Sham matrix
            J=np.zeros((self.nbasis,self.nbasis))
            eri=self.compute_electron_repulsion_tensor()
            
            for i in range(self.nbasis):
                for j in range(self.nbasis):
                    for k in range(self.nbasis):
                        for l in range(self.nbasis):
                            J[i,j]+=P[k,l]*eri[i,k,j,l]
            
            F=H_core+J+V_xc
            F_ortho=S_inv_sqrt.T@F@S_inv_sqrt
            evals,evecs_ortho=np.linalg.eigh(F_ortho)
            C_new=S_inv_sqrt@evecs_ortho
            
            energy=0.5*np.trace(P@(H_core+F))
            energy_hist.append(energy)
            self.iteration_history.append({'iteration':iteration+1,'energy':energy,'method':'dft'})
            
            if iteration>0 and abs(energy_hist[-1]-energy_hist[-2])<1e-6:
                self.converged=True
                return C_new,energy
            
            C=C_new
        
        return C,energy_hist[-1]
    
    def _compute_xc_potential(self,P:np.ndarray,functional:str)->np.ndarray:
        """Compute exchange-correlation potential"""
        V_xc=np.zeros((self.nbasis,self.nbasis))
        
        # Simplified LDA/GGA approximation
        factor=0.7 if functional=='LDA' else 0.8
        for i in range(self.nbasis):
            for j in range(self.nbasis):
                V_xc[i,j]=factor*np.trace(P)/(self.nbasis**2)*P[i,j]
        
        return V_xc
    
    def compute_total_energy(self,C:np.ndarray,n_electrons:int)->float:
        """Compute total energy from density"""
        T=self.compute_kinetic_matrix()
        V=self.compute_nuclear_attraction_matrix()
        H_core=T+V
        
        C_occ=C[:,:n_electrons//2]
        P=2*C_occ@C_occ.T
        
        E_one_electron=np.trace(P@H_core)
        
        # Two-electron energy
        eri=self.compute_electron_repulsion_tensor()
        E_two_electron=0
        for i in range(self.nbasis):
            for j in range(self.nbasis):
                for k in range(self.nbasis):
                    for l in range(self.nbasis):
                        E_two_electron+=0.5*P[i,k]*P[j,l]*(eri[i,j,k,l]-0.5*eri[i,l,k,j])
        
        # Nuclear repulsion
        E_nuc=0
        for i in range(len(self.nuclear_charges)):
            for j in range(i+1,len(self.nuclear_charges)):
                Rij=np.linalg.norm(self.geometry[i]-self.geometry[j])
                E_nuc+=self.nuclear_charges[i]*self.nuclear_charges[j]/Rij
        
        return float(E_one_electron+E_two_electron+E_nuc)
    
    def run_hartree_fock(self,n_electrons:int)->Dict:
        """Run Hartree-Fock calculation"""
        C=np.random.randn(self.nbasis,self.nbasis)
        C,_=np.linalg.qr(C)
        C_final,final_energy=self.scf_iteration(C,n_electrons)
        
        return {
            'converged':self.converged,
            'final_energy':float(final_energy),
            'iterations':len(self.iteration_history),
            'orbital_energies':None,
            'orbitals':C_final,
            'iteration_history':self.iteration_history
        }
    
    def run_dft(self,n_electrons:int,functional:str='LDA')->Dict:
        """Run DFT calculation"""
        C=np.random.randn(self.nbasis,self.nbasis)
        C,_=np.linalg.qr(C)
        C_final,final_energy=self.dft_iteration(C,n_electrons,functional)
        
        return {
            'converged':self.converged,
            'final_energy':float(final_energy),
            'iterations':len(self.iteration_history),
            'functional':functional,
            'orbitals':C_final,
            'iteration_history':self.iteration_history
        }

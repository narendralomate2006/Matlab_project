import sympy as sp
from sympy.integrals.manualintegrate import manualintegrate

def solve_math_problem(input_str, problem_type):
    """
    Core mathematical engine for solving integrals, derivatives, and Beta functions.
    Updated with structured logic for improved accuracy.
    """
    try:
        # Step 1: Input Cleaning
        # Strip 'integrate', 'derivative'
        clean_input = input_str.replace('integrate', '').replace('derivative', '').strip()
        
        # Remove outermost parentheses ONLY if they wrap the entire string
        while clean_input.startswith('(') and clean_input.endswith(')'):
            # Check if these parentheses are a pair
            content = clean_input[1:-1]
            # Simple check for balanced parentheses in content
            balance = 0
            is_pair = True
            for char in content:
                if char == '(': balance += 1
                elif char == ')': balance -= 1
                if balance < 0:
                    is_pair = False
                    break
            if is_pair and balance == 0:
                clean_input = content.strip()
            else:
                break

        # Replace ^ with ** for SymPy
        clean_input = clean_input.replace('^', '**')
        
        # Step 2: Quiz/Arithmetic Check
        # If the problem is from a test or arithmetic section, do not perform calculus
        if problem_type in ['quiz', 'arithmetic']:
            result = sp.simplify(clean_input)
            return {
                'result': str(result),
                'steps': rf"Simplified Result: {sp.latex(result)}",
                'success': True
            }

        if problem_type == 'beta':
            # Beta Logic using lowercase sp.gamma
            parts = [p.strip() for p in clean_input.split(',')]
            if len(parts) != 2:
                raise ValueError("Beta requires two arguments: m, n")
            
            m_val = sp.sympify(parts[0])
            n_val = sp.sympify(parts[1])
            
            # Step-by-step LaTeX derivation
            target_form = r"B(m, n) = \int_0^1 t^{m-1}(1-t)^{n-1} dt"
            exponents = rf"\text{{Identify parameters: }} m = {sp.latex(m_val)}, \quad n = {sp.latex(n_val)}"
            
            # Use lowercase sp.gamma for relationship display and calculation
            gamma_rel = rf"\text{{Use Gamma relationship: }} B(m, n) = \frac{{\Gamma(m)\Gamma(n)}}{{\Gamma(m+n)}} = \frac{{\Gamma({sp.latex(m_val)})\Gamma({sp.latex(n_val)})}}{{\Gamma({sp.latex(m_val+n_val)})}}"
            
            # Calculation strictly using lowercase sp.gamma
            result = (sp.gamma(m_val) * sp.gamma(n_val)) / sp.gamma(m_val + n_val)
            
            steps = rf"{target_form} \\ {exponents} \\ {gamma_rel}"
            
            return {
                'result': sp.latex(result),
                'steps': steps,
                'success': True
            }

        # Step 3: Calculus Parsing (Derivatives and Integrals)
        # Parse expression and potential limits/variables
        if ',' in clean_input:
            # Wrap in parentheses to ensure Tuple parsing if commas are present
            parsed = sp.sympify(f"({clean_input})")
            expr = parsed[0]
            params = parsed[1:]
        else:
            expr = sp.sympify(clean_input)
            params = []

        # Step 4: Derivative Logic
        if problem_type == 'derivative':
            var = params[0] if params else list(expr.free_symbols)[0]
            res = sp.diff(expr, var)
            return {
                'result': sp.latex(res),
                'steps': rf"\frac{{d}}{{d{sp.latex(var)}}} \left( {sp.latex(expr)} \right) = {sp.latex(res)}",
                'success': True
            }

        # Step 5: Integration Logic (Single/Double/Definite)
        else: 
            if not params:
                symbols = list(expr.free_symbols)
                var = symbols[0] if symbols else sp.Symbol('x')
                limits = [var]
            else:
                limits = params
            
            # Double Integration Logic: Nested loop for limits
            final_res = expr
            for lim in limits:
                final_res = sp.integrate(final_res, lim)
            
            # Attempt to generate steps for single integration
            if len(limits) == 1 and not isinstance(limits[0], tuple):
                try:
                    steps = sp.latex(manualintegrate(expr, limits[0]))
                except:
                    steps = rf"\int {sp.latex(expr)} \, d{sp.latex(limits[0])}"
            else:
                steps = "Definite/Double integration completed."
                
            return {
                'result': sp.latex(final_res),
                'steps': steps,
                'success': True
            }
                
    except Exception as e:
        return {'success': False, 'error': str(e)}

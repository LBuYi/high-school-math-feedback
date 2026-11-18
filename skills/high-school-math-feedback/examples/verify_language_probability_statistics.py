"""Exact, self-contained checks for fictional probability/statistics language examples."""
from itertools import permutations, product
from pathlib import Path
import argparse
import sys
sys.dont_write_bytecode=True
import sympy as s
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from math_checks import MathChecks

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    c=MathChecks()
    def eq(qid,key,left,right,assumptions='题设有限等可能样本空间，采用精确有理数'):
        c.equal(qid+'-'+key,left,right,assumptions,key,question_id=qid)
    def yes(qid,key,condition,assumptions='已明确对象与题面条件'):
        c.condition(qid+'-'+key,condition,assumptions,key,question_id=qid)
    def probability(event,omega):
        assert event<=omega and omega
        return s.Rational(len(event),len(omega))

    # Uniform draws without replacement: ordered labelled outcomes are equiprobable.
    omega=set(permutations(('R1','R2','W'),2))
    A={o for o in omega if o[0].startswith('R')}
    B={o for o in omega if o[1].startswith('R')}
    eq('draw','outcome_count',len(omega),6)
    eq('draw','first_red',probability(A,omega),s.Rational(2,3))
    eq('draw','second_red_marginal',probability(B,omega),s.Rational(2,3))
    eq('draw','both_red',probability(A&B,omega),s.Rational(1,3))
    eq('draw','second_red_after_first_red',probability(A&B,omega)/probability(A,omega),s.Rational(1,2))
    eq('draw','correct_product',s.Rational(2,3)*s.Rational(1,2),s.Rational(1,3))
    yes('draw','marginals_not_independent',s.Ne(probability(A&B,omega),probability(A,omega)*probability(B,omega)))

    # Exactly one and at least one in two independent fair trials.
    omega=set(product(('H','T'),repeat=2))
    exactly={o for o in omega if o.count('H')==1}
    at_least={o for o in omega if o.count('H')>=1}
    none={o for o in omega if o.count('H')==0}
    eq('coin','exactly_one',probability(exactly,omega),s.Rational(1,2))
    eq('coin','at_least_one',probability(at_least,omega),s.Rational(3,4))
    yes('coin','extra_outcome',at_least-exactly=={('H','H')})
    eq('coin','complement',probability(at_least,omega),1-probability(none,omega))
    p=s.symbols('p',real=True)
    eq('coin','general_exactly_one',p*(1-p)+(1-p)*p,2*p*(1-p),'两次相互独立且成功概率同为p，0<=p<=1')
    eq('coin','at_least_minus_exactly',1-(1-p)**2-2*p*(1-p),p*p,'两次相互独立且成功概率同为p，0<=p<=1')

    # Disjoint positive-probability events are not independent; zero probability is a real exception.
    omega=set(range(1,7)); A={1}; B={2}
    yes('relation','disjoint',not A&B)
    eq('relation','joint_zero',probability(A&B,omega),0)
    eq('relation','product_positive',probability(A,omega)*probability(B,omega),s.Rational(1,36))
    eq('relation','empty_event_independent',probability(set()&B,omega),probability(set(),omega)*probability(B,omega))
    u,v=s.symbols('u v',positive=True)
    yes('relation','general_positive_product',u*v>0,'P(A)=u>0且P(B)=v>0')

    # Pairwise independence does not justify multiplying three marginal probabilities.
    omega=set(product((0,1),repeat=2))
    events=[{o for o in omega if o[0]==0},{o for o in omega if o[1]==0},
            {o for o in omega if o[0]==o[1]}]
    for i,j in ((0,1),(0,2),(1,2)):
        eq('three',f'pair_{i}_{j}',probability(events[i]&events[j],omega),probability(events[i],omega)*probability(events[j],omega))
    joint=probability(set.intersection(*events),omega)
    prod=s.prod(probability(event,omega) for event in events)
    eq('three','joint',joint,s.Rational(1,4))
    eq('three','marginal_product',prod,s.Rational(1,8))
    yes('three','not_mutual',s.Ne(joint,prod))

    n1,n2=s.symbols('n1 n2',positive=True)
    m1,m2=s.symbols('m1 m2',real=True)
    mean=(n1*m1+n2*m2)/(n1+n2)
    eq('mean','total_sum',mean*(n1+n2),n1*m1+n2*m2,'n1,n2为正数据量，同一变量、单位一致，两组不重叠')
    eq('mean','fictional_merged',mean.subs({n1:10,n2:30,m1:60,m2:80}),75)
    eq('mean','student_unweighted',(60+80)//2,70)
    eq('mean','equal_sizes_case',mean.subs(n2,n1),(m1+m2)/2,'两组数据量相同')
    eq('mean','weight_sum',n1/(n1+n2)+n2/(n1+n2),1,'正数据量之和非零')

    v1,v2=s.symbols('v1 v2',nonnegative=True)
    raw=(n1*(v1+m1*m1)+n2*(v2+m2*m2))/(n1+n2)-mean*mean
    decomposed=(n1*(v1+(m1-mean)**2)+n2*(v2+(m2-mean)**2))/(n1+n2)
    eq('variance','general_decomposition',raw,decomposed,'描述性方差的分母为本组数据量；两组不重叠且单位一致')
    def moments(values):
        mu=s.Rational(sum(values),len(values))
        var=sum((s.Integer(value)-mu)**2 for value in values)/len(values)
        return mu,var
    a=[2,6]; b=[6,9,12]; ma,va=moments(a); mb,vb=moments(b); mab,vab=moments(a+b)
    eq('variance','finite_example_mean',mab,7)
    eq('variance','finite_example_variance',vab,s.Rational(56,5))
    eq('variance','finite_decomposition',decomposed.subs({n1:len(a),n2:len(b),m1:ma,m2:mb,v1:va,v2:vb}),vab)
    eq('variance','zero_within_positive_between',decomposed.subs({n1:1,n2:1,m1:0,m2:2,v1:0,v2:0}),1)
    eq('variance','wrong_within_only',(n1*v1+n2*v2).subs({n1:1,n2:1,v1:0,v2:0})/2,0)

    sample=[10,12,14]
    eq('estimate','sample_mean',moments(sample)[0],12)
    eq('estimate','possible_population_one',moments(sample+[16])[0],13)
    eq('estimate','possible_population_two',moments(sample+[8])[0],11)
    yes('estimate','sample_not_exact_population',s.Ne(moments(sample)[0],moments(sample+[16])[0]))
    c.require_coverage(['draw','coin','relation','three','mean','variance','estimate'])
    if args.report: c.write(args.report)
    c.require_passed()
    import json
    print(json.dumps(c.report()['totals'],ensure_ascii=False))

if __name__=='__main__':
    main()

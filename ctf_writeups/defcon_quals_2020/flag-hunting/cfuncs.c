//b58310a1d83b616fca1491b8ddaa4051. Note the DWORD sized stores at buff 0, 1, and 2.
int * malloc_struct(char input){
    foobar * a = malloc(32);
    a.character = input;  + 0
    a.count = 1; + 4
    a.b = 1; + 8
    a.left = NULL; + 0x10
    a.right = NULL; + 0x18

}

struct foobar{
    char character;
    int count;
    int b;
    foobar * left;
    foobar * right;
}

    A                  B
  /                      \
 B        becomes          A    If and only if A and B are not null, and A->B == B -> B (need to verify equality)// Only need A and B. C gets moved, but could be null
  \                      /
   C                   C

// Really the first rotation. Given a unique name before I figured out what it did
foobar * UNEQ_WOMBAT(foobar * index_a){ //83be5e65d5010b6ce1fd4da060e07888
    foobar * left_child = index_a->left;
    if(left_child == NULL){
        return index_a;
    }
    if(left_child->b != index_a->b){
        foobar * left_childs_right_child = left_child->right;
        index_a->left = left_childs_right_child;
        left_child->right = index_a;
        return left_child;
    }else{
        return index_a;
    }
}

    A                          B
      \                      /   \
        B      becomes     A       C        if and only if A and C have same b value
       / \                  \
      D   C                   D

// Really the second rotation. Given a unique name before I figured out what it did
foobar * UNEQ_UNICORN(foobar * index_a){ //1f7aa429199eac8a7c6017e9e57df7fc
    foobar * right_child = index_a->right;
    if(right_child == NULL){
        return index_a;
    }
    if(right_child->right == NULL){
        return index_a;
    }
    if(right_child->right->b == index_a->b){
        //Since we know the big code block happens the first time it is run, this must be if the values are equal
        foobar * d = index_a->right_child->right_child;
        foobar * b = index_a->right_child;
        index_a -> right_child = d;
        b -> left_child = index_a;
        b->b++;
        return b;
    }
    return index_a;

}

// d670e25f0b1e4b298321e687f777ec14
foobar * beta_check(foobar * index_a, char INDEX_B){
    if(index_a == NULL){ //7e8d3d12f9987acc83634394bb225179
        return malloc_struct(INDEX_B);
    }else{//62c2cd053dfa2c78589308e078cb3740
        char temp = *(char *)index_a;
        if(temp == INDEX_B){
            index_a[1] += 1; //b39fabb14ca48dfa222944f6b24fff4b
        }else{
            if(temp < INDEX_B){ //Go left branch
                beta_check(&index_a[2] ,INDEX_B);
            }
            else if(temp > INDEX_B){ //Go right branch
                beta_check(&index_a[3] ,INDEX_B);
            }
        }

        index_a = UNEQ_WOMBAT(index_a);
        index_a = UNEQ_UNICORN(index_a);

    }

}

//bb9cc4afceb13f7385ca1ada5a386eb2
void check_two(char * buff, int length){
    int * index_a = NULL;
    int INDEX_B = 0;
    while(1){
        char temp = buff[INDEX_B];
        index_a = beta_check(index_a, temp);
        INDEX_B++;
        if(INDEX_B >= length){//Breaks before the last character goes through
            break;
        }
    }
    selective_print(index_a); //called from block df039c4f71bd6ae92ae0b8c80503e5da
}


int main(int argc, char * argv[]){
    //Ignoring initial stuff
    char buff[];
    fopen64(____);
    fread(buff, 1, 0x3c, ___);
    int res = first_checks(buff); //returns 0x39 the first time, searching for the }
    check_two(buff, res); //res is 0x39
    return 0;
}


int first_check(char * buff){
    //1b64d9cc243c25e429b5cca3c5e66c8b
    //Does initial checks on flag -> OOO{>>>> >> >>>>> >>>> >>> >>> >>> >>>> >>>> >>>>>> >>>>>}
    //Where > are unknown chars, each is > 0x60 and <= 0x7b
    return buff.index_of("}"); //not valid c. sue me. returns 0x39
}

//Takes the final malloc'ed buff from before, and does some selective printing
//05ac00e1e7aae89912d1ee1d234e3f19
void selective_print(int * buff){
    Does a walk of the tree and prints out each node. Recurses on left child, self, then recurses on right child
}